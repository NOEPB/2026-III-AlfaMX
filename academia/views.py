from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, TemplateView, UpdateView

from alfabetizacion.models import PerfilUsuario
from alumno.models import Acompanamiento
from .forms import (
    ActividadForm, AdministrarUsuarioCreateForm, AdministrarUsuarioUpdateForm,
    LeccionForm, LoginForm, ModuloForm, RegistroEstudianteForm,
)
from .models import Actividad, Alumno, Leccion, Modulo
from .permissions import AdministradorRequiredMixin, TutorOAdministradorRequiredMixin, es_administrador, es_tutor


class InicioView(LoginRequiredMixin, TemplateView):
    template_name = 'academia/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        modulos = list(Modulo.objects.prefetch_related('lecciones__actividades'))
        # El panel muestra únicamente cifras derivadas de intentos reales guardados.
        from evaluarme.models import Intento
        from django.db.models import Avg, Sum
        intentos = Intento.objects.filter(usuario=usuario)
        actividades_superadas = set(
            intentos.filter(es_correcto=True).values_list('actividad_id', flat=True)
        )
        total_lecciones = 0
        lecciones_completadas = 0
        for modulo in modulos:
            for leccion in modulo.lecciones.all():
                actividades = list(leccion.actividades.all())
                total_lecciones += 1
                if actividades and all(a.pk in actividades_superadas for a in actividades):
                    lecciones_completadas += 1
        metricas = intentos.aggregate(promedio=Avg('puntaje'), segundos=Sum('tiempo_seg'))
        context.update({
            'modulos': modulos,
            'perfil': getattr(usuario, 'perfil', None),
            'es_admin': es_administrador(usuario),
            'es_tutor': es_tutor(usuario),
            'total_modulos': len(modulos),
            'total_lecciones': total_lecciones,
            'total_estudiantes': PerfilUsuario.objects.filter(rol=PerfilUsuario.ROL_ESTUDIANTE).count(),
            'home_total_intentos': intentos.count(),
            'home_promedio': round(metricas['promedio'] or 0),
            'home_minutos': round((metricas['segundos'] or 0) / 60),
            'home_lecciones_completadas': lecciones_completadas,
            'home_porcentaje': round(lecciones_completadas / total_lecciones * 100) if total_lecciones else 0,
        })
        return context


class DetalleModuloView(LoginRequiredMixin, DetailView):
    model = Modulo
    template_name = 'academia/detalle_modulo.html'
    context_object_name = 'modulo'

    def get_queryset(self):
        return Modulo.objects.prefetch_related('lecciones__actividades')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_admin'] = es_administrador(self.request.user)
        return context


class ModuloCreateView(AdministradorRequiredMixin, CreateView):
    model = Modulo
    form_class = ModuloForm
    template_name = 'academia/form_page.html'
    extra_context = {'titulo': 'Crear módulo', 'subtitulo': 'Agrega una nueva sección de aprendizaje.', 'volver_url': reverse_lazy('home')}

    def form_valid(self, form):
        messages.success(self.request, 'El módulo se creó correctamente.')
        return super().form_valid(form)


class ModuloUpdateView(AdministradorRequiredMixin, UpdateView):
    model = Modulo
    form_class = ModuloForm
    template_name = 'academia/form_page.html'
    extra_context = {'titulo': 'Editar módulo', 'subtitulo': 'Actualiza la información de esta sección.', 'volver_url': reverse_lazy('home')}

    def form_valid(self, form):
        messages.success(self.request, 'El módulo se actualizó correctamente.')
        return super().form_valid(form)


class ModuloDeleteView(AdministradorRequiredMixin, DeleteView):
    model = Modulo
    template_name = 'academia/confirmar_eliminacion.html'
    success_url = reverse_lazy('home')
    extra_context = {'volver_url': reverse_lazy('home'), 'aviso_dependencias': 'También se eliminarán las lecciones y actividades que pertenezcan a este módulo.'}

    def form_valid(self, form):
        messages.success(self.request, 'El módulo y su contenido relacionado se eliminaron.')
        return super().form_valid(form)


class LeccionCreateView(AdministradorRequiredMixin, CreateView):
    model = Leccion
    form_class = LeccionForm
    template_name = 'academia/form_page.html'
    extra_context = {'titulo': 'Crear lección', 'subtitulo': 'Agrega una lección a un módulo.', 'volver_url': reverse_lazy('home')}

    def get_initial(self):
        initial = super().get_initial()
        modulo_id = self.request.GET.get('modulo')
        if modulo_id and Modulo.objects.filter(pk=modulo_id).exists():
            initial['modulo'] = modulo_id
        return initial

    def get_success_url(self):
        return reverse('detalle_modulo', kwargs={'pk': self.object.modulo_id})

    def form_valid(self, form):
        messages.success(self.request, 'La lección se creó correctamente.')
        return super().form_valid(form)


class LeccionUpdateView(AdministradorRequiredMixin, UpdateView):
    model = Leccion
    form_class = LeccionForm
    template_name = 'academia/form_page.html'
    extra_context = {'titulo': 'Editar lección', 'subtitulo': 'Modifica el módulo, título o nivel de la lección.', 'volver_url': reverse_lazy('home')}

    def get_success_url(self):
        return reverse('detalle_modulo', kwargs={'pk': self.object.modulo_id})

    def form_valid(self, form):
        messages.success(self.request, 'La lección se actualizó correctamente.')
        return super().form_valid(form)


class LeccionDeleteView(AdministradorRequiredMixin, DeleteView):
    model = Leccion
    template_name = 'academia/confirmar_eliminacion.html'

    def get_success_url(self):
        return reverse('detalle_modulo', kwargs={'pk': self.object.modulo_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['aviso_dependencias'] = 'También se eliminarán todas las actividades de esta lección.'
        context['volver_url'] = reverse('detalle_modulo', kwargs={'pk': self.object.modulo_id})
        return context

    def form_valid(self, form):
        messages.success(self.request, 'La lección se eliminó correctamente.')
        return super().form_valid(form)


class ActividadCreateView(AdministradorRequiredMixin, CreateView):
    model = Actividad
    form_class = ActividadForm
    template_name = 'academia/form_page.html'
    extra_context = {'titulo': 'Crear actividad', 'subtitulo': 'Diseña un ejercicio para una lección.', 'volver_url': reverse_lazy('home')}

    def get_initial(self):
        initial = super().get_initial()
        leccion_id = self.request.GET.get('leccion')
        if leccion_id and Leccion.objects.filter(pk=leccion_id).exists():
            initial['leccion'] = leccion_id
        return initial

    def get_success_url(self):
        return reverse('detalle_modulo', kwargs={'pk': self.object.leccion.modulo_id})

    def form_valid(self, form):
        messages.success(self.request, 'La actividad se creó correctamente.')
        return super().form_valid(form)


class ActividadUpdateView(AdministradorRequiredMixin, UpdateView):
    model = Actividad
    form_class = ActividadForm
    template_name = 'academia/form_page.html'
    extra_context = {'titulo': 'Editar actividad', 'subtitulo': 'Actualiza las instrucciones y el contenido del ejercicio.', 'volver_url': reverse_lazy('home')}

    def get_success_url(self):
        return reverse('detalle_modulo', kwargs={'pk': self.object.leccion.modulo_id})


class ActividadDeleteView(AdministradorRequiredMixin, DeleteView):
    model = Actividad
    template_name = 'academia/confirmar_eliminacion.html'

    def get_success_url(self):
        return reverse('detalle_modulo', kwargs={'pk': self.object.leccion.modulo_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['aviso_dependencias'] = 'Los intentos y trazos relacionados con esta actividad también se eliminarán.'
        context['volver_url'] = reverse('detalle_modulo', kwargs={'pk': self.object.leccion.modulo_id})
        return context


class ListaAlumnosView(TutorOAdministradorRequiredMixin, TemplateView):
    template_name = 'academia/lista_alumnos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        perfiles = PerfilUsuario.objects.filter(
            rol=PerfilUsuario.ROL_ESTUDIANTE
        ).select_related('user', 'escuela').order_by('user__first_name', 'user__username')
        es_admin = es_administrador(self.request.user)
        if not es_admin:
            ids = Acompanamiento.objects.filter(
                tutor=self.request.user, estado='activo'
            ).values_list('estudiante_id', flat=True)
            perfiles = perfiles.filter(user_id__in=ids)
        busqueda = self.request.GET.get('q', '').strip()
        if busqueda:
            from django.db.models import Q
            perfiles = perfiles.filter(
                Q(user__username__icontains=busqueda)
                | Q(user__first_name__icontains=busqueda)
                | Q(user__last_name__icontains=busqueda)
                | Q(user__email__icontains=busqueda)
            )
        context.update({
            'perfiles': perfiles,
            'busqueda': busqueda,
            'es_admin': es_admin,
            'registros_anteriores': Alumno.objects.all() if es_admin else Alumno.objects.none(),
        })
        return context


class ListaUsuariosView(AdministradorRequiredMixin, ListView):
    model = User
    template_name = 'academia/gestion_usuarios.html'
    context_object_name = 'usuarios'
    paginate_by = 25

    def get_queryset(self):
        qs = User.objects.select_related('perfil').prefetch_related('groups').order_by('username')
        termino = self.request.GET.get('q', '').strip()
        if termino:
            from django.db.models import Q
            qs = qs.filter(
                Q(username__icontains=termino) | Q(first_name__icontains=termino)
                | Q(last_name__icontains=termino) | Q(email__icontains=termino)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['busqueda'] = self.request.GET.get('q', '').strip()
        context['total_usuarios'] = User.objects.count()
        context['total_estudiantes'] = PerfilUsuario.objects.filter(rol=PerfilUsuario.ROL_ESTUDIANTE).count()
        context['total_tutores'] = PerfilUsuario.objects.filter(rol=PerfilUsuario.ROL_TUTOR).count()
        context['total_administradores'] = PerfilUsuario.objects.filter(rol=PerfilUsuario.ROL_ADMIN).count()
        from django.db.models import Count
        context['correos_duplicados'] = list(
            User.objects.exclude(email='').values('email')
            .annotate(total=Count('id')).filter(total__gt=1)
            .values_list('email', flat=True)
        )
        return context


class UsuarioCreateView(AdministradorRequiredMixin, CreateView):
    model = User
    form_class = AdministrarUsuarioCreateForm
    template_name = 'academia/form_page.html'
    success_url = reverse_lazy('gestion_usuarios')
    extra_context = {'titulo': 'Crear usuario', 'subtitulo': 'Crea una cuenta y asigna su rol.', 'volver_url': reverse_lazy('gestion_usuarios')}

    def form_valid(self, form):
        messages.success(self.request, 'La cuenta se creó correctamente.')
        return super().form_valid(form)


class UsuarioUpdateView(AdministradorRequiredMixin, UpdateView):
    model = User
    form_class = AdministrarUsuarioUpdateForm
    template_name = 'academia/form_page.html'
    success_url = reverse_lazy('gestion_usuarios')
    extra_context = {'titulo': 'Editar usuario', 'subtitulo': 'Actualiza sus datos, rol o estado de acceso.', 'volver_url': reverse_lazy('gestion_usuarios')}

    def get_queryset(self):
        return User.objects.exclude(is_superuser=True)

    def form_valid(self, form):
        messages.success(self.request, 'Los datos del usuario se actualizaron.')
        return super().form_valid(form)


class UsuarioDeleteView(AdministradorRequiredMixin, DeleteView):
    model = User
    template_name = 'academia/confirmar_eliminacion.html'
    success_url = reverse_lazy('gestion_usuarios')

    def get_queryset(self):
        return User.objects.exclude(is_superuser=True).exclude(pk=self.request.user.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['volver_url'] = reverse_lazy('gestion_usuarios')
        context['aviso_dependencias'] = 'Se eliminará la cuenta. Esta operación también elimina su perfil y sus datos dependientes.'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'La cuenta se eliminó correctamente.')
        return super().form_valid(form)


class RegistroView(FormView):
    template_name = 'academia/registro.html'
    form_class = RegistroEstudianteForm
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        from django.contrib.auth import login
        login(self.request, user)
        messages.success(self.request, 'Tu cuenta se creó. ¡Comencemos a aprender!')
        return super().form_valid(form)


# El login se mantiene como vista basada en clase de Django y recibe LoginForm.
