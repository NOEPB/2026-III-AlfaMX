from django.contrib.auth import views as auth_views
from django.urls import path

from .forms import LoginForm
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='academia/login.html', authentication_form=LoginForm,
        redirect_authenticated_user=True,
    ), name='login'),
    path('registro/', views.RegistroView.as_view(), name='registro'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('', views.InicioView.as_view(), name='home'),
    path('modulo/<int:pk>/', views.DetalleModuloView.as_view(), name='detalle_modulo'),
    path('modulo/crear/', views.ModuloCreateView.as_view(), name='crear_modulo'),
    path('modulo/<int:pk>/editar/', views.ModuloUpdateView.as_view(), name='editar_modulo'),
    path('modulo/<int:pk>/eliminar/', views.ModuloDeleteView.as_view(), name='eliminar_modulo'),

    path('leccion/crear/', views.LeccionCreateView.as_view(), name='crear_leccion'),
    path('leccion/<int:pk>/editar/', views.LeccionUpdateView.as_view(), name='editar_leccion'),
    path('leccion/<int:pk>/eliminar/', views.LeccionDeleteView.as_view(), name='eliminar_leccion'),
    path('actividad/crear/', views.ActividadCreateView.as_view(), name='crear_actividad'),
    path('actividad/<int:pk>/editar/', views.ActividadUpdateView.as_view(), name='editar_actividad'),
    path('actividad/<int:pk>/eliminar/', views.ActividadDeleteView.as_view(), name='eliminar_actividad'),

    path('alumnos/', views.ListaAlumnosView.as_view(), name='lista_alumnos'),
    path('usuarios/', views.ListaUsuariosView.as_view(), name='gestion_usuarios'),
    path('usuarios/crear/', views.UsuarioCreateView.as_view(), name='crear_usuario'),
    path('usuarios/<int:pk>/editar/', views.UsuarioUpdateView.as_view(), name='editar_usuario'),
    path('usuarios/<int:pk>/eliminar/', views.UsuarioDeleteView.as_view(), name='eliminar_usuario'),
]
