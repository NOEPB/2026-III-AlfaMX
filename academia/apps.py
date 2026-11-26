from django.apps import AppConfig


class AcademiaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'academia'

    def ready(self):
        from . import signals  # noqa: F401
