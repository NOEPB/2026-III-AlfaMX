from django.contrib import admin
from .models import Actividad, Alumno, Leccion, Modulo


class LeccionInline(admin.TabularInline):
    model = Leccion
    extra = 0


class ActividadInline(admin.TabularInline):
    model = Actividad
    extra = 0


@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'orden', 'total_lecciones')
    search_fields = ('nombre',)
    ordering = ('orden', 'nombre')
    inlines = (LeccionInline,)

    @admin.display(description='Lecciones')
    def total_lecciones(self, obj):
        return obj.total_lecciones


@admin.register(Leccion)
class LeccionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'modulo', 'nivel', 'orden')
    list_filter = ('modulo', 'nivel')
    search_fields = ('titulo', 'modulo__nombre')
    inlines = (ActividadInline,)


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'leccion', 'orden')
    list_filter = ('leccion__modulo', 'tipo')
    search_fields = ('instruccion_audio', 'leccion__titulo')


@admin.register(Alumno)
class AlumnoHistoricoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'edad', 'categoria_edad', 'fecha_registro')
    search_fields = ('nombre',)
    readonly_fields = ('nombre', 'edad', 'fecha_registro')
