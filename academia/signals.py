from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from alfabetizacion.models import PerfilUsuario
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        rol = PerfilUsuario.ROL_ADMIN if instance.is_superuser else PerfilUsuario.ROL_ESTUDIANTE
        PerfilUsuario.objects.get_or_create(user=instance, defaults={'rol': rol})


@receiver(post_migrate)
def configurar_grupos(sender, **kwargs):
    """Crea roles iniciales y asigna permisos únicamente desde el servidor."""
    grupos = {}
    for nombre in ('Administrador', 'Tutor', 'Estudiante'):
        grupos[nombre], _ = Group.objects.get_or_create(name=nombre)

    permisos_admin = Permission.objects.filter(
        content_type__app_label='academia',
        content_type__model__in=('modulo', 'leccion', 'actividad'),
    )
    permisos_admin |= Permission.objects.filter(
        content_type__app_label='auth',
        codename__in=('view_user', 'add_user', 'change_user', 'delete_user'),
    )
    permisos_admin |= Permission.objects.filter(
        content_type__app_label='alfabetizacion',
        content_type__model='perfilusuario',
    )
    grupos['Administrador'].permissions.set(permisos_admin.distinct())

    permisos_tutor = Permission.objects.filter(
        content_type__app_label='academia',
        codename__in=('view_modulo', 'view_leccion', 'view_actividad'),
    )
    permisos_tutor |= Permission.objects.filter(
        content_type__app_label='alumno',
        content_type__model__in=('acompanamiento', 'nota', 'sesion'),
        codename__startswith='view_',
    )
    grupos['Tutor'].permissions.set(permisos_tutor.distinct())
    grupos['Estudiante'].permissions.set(
        Permission.objects.filter(
            content_type__app_label='academia',
            codename__in=('view_modulo', 'view_leccion', 'view_actividad'),
        )
    )

    # Mantiene el rol del perfil y el grupo de Django sincronizados para
    # las cuentas que ya existían antes de agregar el nuevo panel.
    for perfil in PerfilUsuario.objects.select_related('user').all():
        if perfil.user.is_superuser:
            continue
        grupo = grupos.get(perfil.get_rol_display())
        if grupo and not perfil.user.groups.filter(pk=grupo.pk).exists():
            perfil.user.groups.set([grupo])
