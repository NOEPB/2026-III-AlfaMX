import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from academia.models import Actividad, Leccion, Modulo
from alumno.models import Acompanamiento
from .models import Intento, Trazo
from .scoring import calcular_precision, expected_strokes


class EvaluacionDeTrazoTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(
            username='lectora', password='ClaveSegura123!', email='lectora@example.com'
        )
        self.modulo = Modulo.objects.create(nombre='Trazo', orden=3)
        self.leccion = Leccion.objects.create(
            modulo=self.modulo, titulo='Traza la A', nivel=1, orden=1
        )
        self.actividad = Actividad.objects.create(
            leccion=self.leccion, tipo='trazo',
            instruccion_audio='Sigue la forma de la A.',
            contenido={'objetivo': 'A', 'letra': 'A'}, orden=1,
        )

    def _points_for_target(self, target='A'):
        points = []
        index = 0
        for stroke_number, stroke in enumerate(expected_strokes(target)):
            for x, y in stroke:
                points.append({'x': x, 'y': y, 't': index * 20, 'stroke': stroke_number})
                index += 1
        return points

    def test_plantilla_vectorial_da_puntuacion_alta_a_un_trazo_igual(self):
        score = calcular_precision('A', self._points_for_target())
        self.assertGreaterEqual(score, 90)

    def test_pantalla_practica_muestra_guia_con_inicio_y_recorrido(self):
        self.client.login(username='lectora', password='ClaveSegura123!')
        response = self.client.get(reverse('realizar_actividad', args=[self.actividad.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['guia_disponible'])
        self.assertGreaterEqual(len(response.context['guia_trazo']), 1)
        self.assertContains(response, 'id="strokeGuide"')
        self.assertContains(response, 'id="replayGuide"')
        self.assertContains(response, 'Empieza en el punto verde')

    def test_guarda_intento_y_coordenadas_de_trazo(self):
        self.client.login(username='lectora', password='ClaveSegura123!')
        payload = {
            'coordenadas': self._points_for_target(),
            'tiempo_seg': 18,
            'usos_audio': 2,
        }
        response = self.client.post(
            reverse('guardar_intento', args=[self.actividad.pk]),
            data=json.dumps(payload), content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['ok'])
        self.assertEqual(Intento.objects.filter(usuario=self.usuario).count(), 1)
        trazo = Trazo.objects.get(intento__usuario=self.usuario)
        self.assertEqual(trazo.caracter_objetivo, 'A')
        self.assertGreaterEqual(trazo.precision, 90)
        self.assertEqual(trazo.coordenadas[0]['stroke'], 0)

    def test_acepta_trazo_correcto_con_mas_de_2500_muestras(self):
        """Un lápiz digital puede enviar más de 2500 muestras en un dibujo."""
        self.client.login(username='lectora', password='ClaveSegura123!')
        coordinates = self._points_for_target()
        last_point = dict(coordinates[-1])
        while len(coordinates) <= 2600:
            extra = dict(last_point)
            extra['t'] = len(coordinates) * 4
            coordinates.append(extra)

        response = self.client.post(
            reverse('guardar_intento', args=[self.actividad.pk]),
            data=json.dumps({'coordenadas': coordinates, 'tiempo_seg': 20, 'usos_audio': 0}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200, response.content.decode())
        self.assertTrue(response.json()['ok'])
        self.assertEqual(Intento.objects.filter(usuario=self.usuario).count(), 1)

    def test_limite_alto_de_seguridad_tiene_mensaje_especifico(self):
        self.client.login(username='lectora', password='ClaveSegura123!')
        response = self.client.post(
            reverse('guardar_intento', args=[self.actividad.pk]),
            data=json.dumps({'coordenadas': [{}] * 8001}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('demasiadas muestras', response.json()['mensaje'])

    def test_pantalla_simplifica_muestras_antes_de_enviar(self):
        self.client.login(username='lectora', password='ClaveSegura123!')
        response = self.client.get(reverse('realizar_actividad', args=[self.actividad.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'MAX_SUBMISSION_POINTS = 1800')
        self.assertContains(response, 'function buildSubmissionPoints()')
        self.assertContains(response, 'coordenadas: submissionPoints')

    def test_no_permite_guardar_sin_iniciar_sesion(self):
        response = self.client.post(
            reverse('guardar_intento', args=[self.actividad.pk]),
            data='{}', content_type='application/json',
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Intento.objects.count(), 0)

    def test_progreso_muestra_actividad_completada(self):
        self.client.login(username='lectora', password='ClaveSegura123!')
        Intento.objects.create(
            usuario=self.usuario, actividad=self.actividad,
            es_correcto=True, puntaje=90, tiempo_seg=30, usos_audio=1,
        )
        response = self.client.get(reverse('mi_progreso'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['actividades_completadas'], 1)
        self.assertEqual(response.context['lecciones_completadas'], 1)

    def test_tutor_solo_puede_ver_alumno_vinculado(self):
        tutor = User.objects.create_user(username='tutor', password='ClaveSegura123!')
        tutor.perfil.rol = 'tutor'
        tutor.perfil.save()
        Acompanamiento.objects.create(tutor=tutor, estudiante=self.usuario, estado='activo')
        self.client.login(username='tutor', password='ClaveSegura123!')
        response = self.client.get(reverse('progreso_usuario', args=[self.usuario.pk]))
        self.assertEqual(response.status_code, 200)
        outsider = User.objects.create_user(username='fuera', password='ClaveSegura123!')
        response = self.client.get(reverse('progreso_usuario', args=[outsider.pk]))
        self.assertEqual(response.status_code, 403)
