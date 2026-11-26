from django.contrib import admin
from .models import Intento, Trazo


class TrazoInline(admin.TabularInline):
    model = Trazo
    extra = 0
    readonly_fields = ('caracter_objetivo', 'precision', 'coordenadas')


@admin.register(Intento)
class IntentoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'actividad', 'puntaje', 'es_correcto', 'tiempo_seg', 'usos_audio', 'fecha_hora')
    list_filter = ('es_correcto', 'actividad__leccion__modulo', 'fecha_hora')
    search_fields = ('usuario__username', 'usuario__first_name', 'actividad__leccion__titulo')
    readonly_fields = ('fecha_hora',)
    inlines = (TrazoInline,)


@admin.register(Trazo)
class TrazoAdmin(admin.ModelAdmin):
    list_display = ('caracter_objetivo', 'precision', 'intento',)
    search_fields = ('caracter_objetivo', 'intento__usuario__username')
    readonly_fields = ('coordenadas',)
