from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('academia/', include('academia.urls')),
    path('evaluarme/', include('evaluarme.urls')),
    path('', RedirectView.as_view(url='/academia/', permanent=False)),
]
