from datetime import date

from django.contrib.auth.models import User
from django.db import models


class Estado(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Escuela(models.Model):
    nombre = models.CharField(max_length=150)
    tipo = models.CharField(max_length=50)
    estado = models.ForeignKey(
        Estado, on_delete=models.PROTECT, related_name='escuelas'
    )
    municipio = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class PerfilUsuario(models.Model):
    ROL_ESTUDIANTE = 'estudiante'
    ROL_TUTOR = 'tutor'
    ROL_ADMIN = 'administrador'
    ROLES = [
        (ROL_ESTUDIANTE, 'Estudiante'),
        (ROL_TUTOR, 'Tutor'),
        (ROL_ADMIN, 'Administrador'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='perfil'
    )
    rol = models.CharField(
        max_length=20, choices=ROLES, default=ROL_ESTUDIANTE
    )
    fecha_nacimiento = models.DateField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    escuela = models.ForeignKey(
        Escuela, on_delete=models.SET_NULL, null=True, blank=True
    )
    acepto_aviso_privacidad = models.BooleanField(default=False)
    autorizacion_tutor = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'perfil de usuario'
        verbose_name_plural = 'perfiles de usuario'

    def __str__(self):
        return f'{self.user.username} ({self.get_rol_display()})'

    @property
    def edad(self):
        if not self.fecha_nacimiento:
            return None
        hoy = date.today()
        return hoy.year - self.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    @property
    def categoria_edad(self):
        if self.edad is None:
            return 'Sin fecha de nacimiento'
        return 'Adulto' if self.edad >= 18 else 'Menor de edad'
