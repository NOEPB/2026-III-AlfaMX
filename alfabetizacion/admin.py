from django.contrib import admin
from .models import Escuela, Estado, PerfilUsuario


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol', 'fecha_nacimiento', 'fecha_registro', 'acepto_aviso_privacidad', 'autorizacion_tutor')
    list_filter = ('rol', 'acepto_aviso_privacidad', 'autorizacion_tutor')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')


admin.site.register(Estado)
admin.site.register(Escuela)
