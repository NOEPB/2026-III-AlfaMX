import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Avg, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, TemplateView

from academia.models import Actividad, Modulo
from academia.permissions import es_administrador, es_tutor
from alumno.models import Acompanamiento
from .models import Intento, Trazo
from .scoring import calcular_precision, expected_strokes, normalizar_objetivo


class RealizarActividadView(LoginRequiredMixin, DetailView):
    model = Actividad
    pk_url_kwarg = 'actividad_id'
    template_name = 'evaluarme/realizar_actividad.html'
    context_object_name = 'actividad'

    def get_queryset(self):
        return Actividad.objects.select_related('leccion__modulo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contenido = self.object.contenido or {}
        objetivo = (contenido.get('objetivo') or contenido.get('palabra')
                    or contenido.get('letra') or 'A')
        objetivo = str(objetivo).strip().upper()
        try:
            guia_trazo = expected_strokes(objetivo)
        except ValueError:
            # Algunos contenidos antiguos pueden no tener una plantilla vectorial.
            # La actividad se sigue mostrando, pero sin inventar un recorrido.
            guia_trazo = []

        context.update({
            'objetivo_trazo': objetivo,
            'guia_trazo': guia_trazo,
            'guia_disponible': bool(guia_trazo),
            'imagen_emoji': contenido.get('imagen_emoji', '✍️'),
            'descripcion_visual': contenido.get('descripcion_visual', 'Mira la forma y trázala con calma.'),
            'intentos_previos': Intento.objects.filter(
                usuario=self.request.user, actividad=self.object
            ).count(),
        })
        return context


@method_decorator(require_POST, name='dispatch')
class GuardarIntentoView(LoginRequiredMixin, View):
    """Valida el trazo, calcula una precisión orientativa y guarda el intento."""

    # Los navegadores modernos pueden entregar muchas muestras coalescidas
    # cuando se usa lápiz digital o pantallas de alta frecuencia. El cliente
    # simplifica el trazo antes de enviarlo, pero el servidor conserva un
    # límite amplio como protección ante peticiones anormalmente grandes.
    MAX_POINTS = 8000

    def post(self, request, actividad_id):
        actividad = get_object_or_404(
            Actividad.objects.select_related('leccion__modulo'), pk=actividad_id
        )
        if actividad.tipo != 'trazo':
            return JsonResponse({'ok': False, 'mensaje': 'Esta actividad no es de tipo trazo.'}, status=400)

        try:
            payload = json.loads(request.body.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return JsonResponse({'ok': False, 'mensaje': 'No pude leer el dibujo. Inténtalo otra vez.'}, status=400)
        if not isinstance(payload, dict):
            return JsonResponse({'ok': False, 'mensaje': 'Los datos de la práctica no son válidos.'}, status=400)

        coordinates = payload.get('coordenadas')
        if not isinstance(coordinates, list) or len(coordinates) < 2:
            return JsonResponse({
                'ok': False,
                'mensaje': 'No recibí un trazo completo. Dibuja una línea antes de terminar.',
            }, status=400)
        if len(coordinates) > self.MAX_POINTS:
            return JsonResponse({
                'ok': False,
                'mensaje': 'El trazo contiene demasiadas muestras. Presiona Borrar y vuelve a intentarlo con movimientos más cortos.',
            }, status=400)

        clean_coordinates = []
        try:
            for point in coordinates:
                x = float(point['x'])
                y = float(point['y'])
                elapsed = max(0, min(3600000, int(point.get('t', 0))))
                stroke = max(0, min(100, int(point.get('stroke', 0))))
                if not (-0.5 <= x <= 1.5 and -0.5 <= y <= 1.5):
                    raise ValueError
                clean_coordinates.append({'x': round(x, 4), 'y': round(y, 4), 't': elapsed, 'stroke': stroke})
        except (KeyError, TypeError, ValueError, OverflowError):
            return JsonResponse({'ok': False, 'mensaje': 'Los datos del trazo no son válidos.'}, status=400)

        contenido = actividad.contenido or {}
        target = (contenido.get('objetivo') or contenido.get('palabra')
                  or contenido.get('letra') or 'A')
        target = str(target).strip().upper()
        try:
            if not normalizar_objetivo(target):
                raise ValueError('No hay una guía compatible para evaluar este ejercicio.')
            precision = calcular_precision(target, clean_coordinates)
        except ValueError as error:
            return JsonResponse({'ok': False, 'mensaje': str(error)}, status=400)

        try:
            tiempo_seg = max(0, min(3600, int(payload.get('tiempo_seg', 0) or 0)))
            usos_audio = max(0, min(100, int(payload.get('usos_audio', 0) or 0)))
        except (TypeError, ValueError, OverflowError):
            return JsonResponse({'ok': False, 'mensaje': 'Los datos de tiempo o audio no son válidos.'}, status=400)
        correcto = precision >= 65
        if precision >= 85:
            mensaje = '¡Excelente! Tu trazo siguió muy bien la guía.'
        elif precision >= 65:
            mensaje = '¡Muy bien! Ya reconoces la forma. Puedes repetir para mejorar.'
        elif precision >= 40:
            mensaje = 'Vas avanzando. Escucha otra vez y sigue la guía con calma.'
        else:
            mensaje = 'Inténtalo otra vez. Sigue la forma de arriba poco a poco.'

        with transaction.atomic():
            intento = Intento.objects.create(
                usuario=request.user,
                actividad=actividad,
                es_correcto=correcto,
                puntaje=precision,
                tiempo_seg=tiempo_seg,
                usos_audio=usos_audio,
            )
            Trazo.objects.create(
                intento=intento,
                caracter_objetivo=target[:10],
                coordenadas=clean_coordinates,
                precision=precision,
            )

        return JsonResponse({
            'ok': True,
            'intento_id': intento.pk,
            'puntaje': precision,
            'es_correcto': correcto,
            'mensaje': mensaje,
            'total_intentos': Intento.objects.filter(usuario=request.user, actividad=actividad).count(),
        })


class ProgresoView(LoginRequiredMixin, TemplateView):
    template_name = 'evaluarme/progreso.html'

    def get_target_user(self):
        usuario_id = self.kwargs.get('usuario_id')
        if not usuario_id or int(usuario_id) == self.request.user.pk:
            return self.request.user
        if es_administrador(self.request.user):
            return get_object_or_404(User, pk=usuario_id)
        if es_tutor(self.request.user) and Acompanamiento.objects.filter(
            tutor=self.request.user, estudiante_id=usuario_id, estado='activo'
        ).exists():
            return get_object_or_404(User, pk=usuario_id)
        raise PermissionDenied('Solo puedes consultar tu propio progreso o el de estudiantes vinculados contigo.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        target_user = self.get_target_user()
        intentos = Intento.objects.filter(usuario=target_user).select_related(
            'actividad__leccion__modulo'
        )
        aggregate = intentos.aggregate(promedio=Avg('puntaje'), segundos=Sum('tiempo_seg'))
        completed_ids = set(intentos.filter(es_correcto=True).values_list(
            'actividad_id', flat=True
        ).distinct())

        module_stats = []
        total_lessons = 0
        completed_lessons = 0
        for modulo in Modulo.objects.prefetch_related('lecciones__actividades'):
            lessons = []
            module_complete = 0
            for leccion in modulo.lecciones.all():
                activities = list(leccion.actividades.all())
                done = bool(activities) and all(a.pk in completed_ids for a in activities)
                lessons.append({
                    'leccion': leccion,
                    'total_actividades': len(activities),
                    'completada': done,
                })
                module_complete += int(done)
            total = len(lessons)
            total_lessons += total
            completed_lessons += module_complete
            module_stats.append({
                'modulo': modulo,
                'lecciones': lessons,
                'total_lecciones': total,
                'lecciones_completadas': module_complete,
                'porcentaje': round(module_complete / total * 100) if total else 0,
            })

        context.update({
            'alumno': target_user,
            'es_otro_usuario': target_user.pk != self.request.user.pk,
            'total_intentos': intentos.count(),
            'actividades_completadas': len(completed_ids),
            'total_actividades': Actividad.objects.count(),
            'promedio': round(aggregate['promedio'] or 0, 1),
            'minutos_practicados': round((aggregate['segundos'] or 0) / 60, 1),
            'lecciones_completadas': completed_lessons,
            'total_lecciones': total_lessons,
            'porcentaje_general': round(completed_lessons / total_lessons * 100) if total_lessons else 0,
            'modulos_progreso': module_stats,
            'ultimos_intentos': intentos.order_by('-fecha_hora')[:10],
        })
        return context
