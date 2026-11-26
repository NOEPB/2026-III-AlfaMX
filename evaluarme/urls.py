from django.urls import path
from .views import GuardarIntentoView, ProgresoView, RealizarActividadView

urlpatterns = [
    path('progreso/', ProgresoView.as_view(), name='mi_progreso'),
    path('progreso/alumno/<int:usuario_id>/', ProgresoView.as_view(), name='progreso_usuario'),
    path('<int:actividad_id>/guardar/', GuardarIntentoView.as_view(), name='guardar_intento'),
    path('<int:actividad_id>/', RealizarActividadView.as_view(), name='realizar_actividad'),
]
