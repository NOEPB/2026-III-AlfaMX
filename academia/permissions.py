from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from alfabetizacion.models import PerfilUsuario


def es_administrador(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.groups.filter(name='Administrador').exists():
        return True
    try:
        return user.perfil.rol == PerfilUsuario.ROL_ADMIN
    except PerfilUsuario.DoesNotExist:
        return False


def es_tutor(user):
    if not user.is_authenticated:
        return False
    try:
        return user.perfil.rol == PerfilUsuario.ROL_TUTOR
    except PerfilUsuario.DoesNotExist:
        return user.groups.filter(name='Tutor').exists()


class AdministradorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    permission_denied_message = 'Solo el personal administrador puede realizar esta acción.'

    def test_func(self):
        return es_administrador(self.request.user)


class TutorOAdministradorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return es_administrador(self.request.user) or es_tutor(self.request.user)
