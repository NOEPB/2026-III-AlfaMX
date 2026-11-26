from django.db import migrations


def normalizar_tipos(apps, schema_editor):
    Actividad = apps.get_model('academia', 'Actividad')
    equivalencias = {
        'trazo': ('Trazo', 'TRAZO', 'trazado'),
        'imagen_palabra': ('imagen-palabra', 'asociacion imagen-palabra'),
        'discriminacion_auditiva': ('discriminación auditiva', 'Discriminación auditiva'),
        'seleccion_multiple': ('selección múltiple', 'Seleccion múltiple'),
        'completar_palabra': ('completar palabra', 'Completar palabra'),
    }
    for nuevo, anteriores in equivalencias.items():
        Actividad.objects.filter(tipo__in=anteriores).update(tipo=nuevo)


class Migration(migrations.Migration):
    dependencies = [
        ('academia', '0003_alter_actividad_options_alter_alumno_options_and_more'),
    ]

    operations = [
        migrations.RunPython(normalizar_tipos, migrations.RunPython.noop),
    ]
