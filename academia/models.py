from django.db import models
from django.urls import reverse


class Modulo(models.Model):
    nombre = models.CharField(max_length=100)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('orden', 'nombre')
        verbose_name = 'módulo'
        verbose_name_plural = 'módulos'

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('detalle_modulo', args=[self.pk])

    @property
    def total_lecciones(self):
        return self.lecciones.count()

    @property
    def icono_visual(self):
        iconos = {
            'vocales': '🔤', 'sílabas': '🧩', 'trazo': '✍️',
            'números': '🔢', 'colores': '🎨', 'palabras': '📖',
        }
        return iconos.get(self.nombre.strip().lower(), '📚')

    @property
    def imagen_path(self):
        """Ruta de la ilustración del módulo; no requiere migración."""
        clave = self.nombre.strip().lower()
        imagenes = {
            'vocales': 'vocales',
            'sílabas': 'silabas', 'silabas': 'silabas',
            'trazo': 'trazo',
            'números': 'numeros', 'numeros': 'numeros',
            'colores': 'colores',
            'palabras': 'palabras',
        }
        archivo = imagenes.get(clave, 'palabras')
        return f'academia/img/modulos/{archivo}.webp'


class Leccion(models.Model):
    modulo = models.ForeignKey(
        Modulo, related_name='lecciones', on_delete=models.CASCADE
    )
    titulo = models.CharField(max_length=200)
    nivel = models.PositiveIntegerField(default=1)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('orden', 'titulo')
        verbose_name = 'lección'
        verbose_name_plural = 'lecciones'

    def __str__(self):
        return f'{self.modulo.nombre} - {self.titulo}'

    @property
    def total_actividades(self):
        return self.actividades.count()


class Actividad(models.Model):
    TIPOS = [
        ('imagen_palabra', 'Asociación imagen-palabra'),
        ('discriminacion_auditiva', 'Discriminación auditiva'),
        ('seleccion_multiple', 'Selección múltiple'),
        ('completar_palabra', 'Completar palabra'),
        ('trazo', 'Trazo'),
    ]

    leccion = models.ForeignKey(
        Leccion, related_name='actividades', on_delete=models.CASCADE
    )
    tipo = models.CharField(max_length=50, choices=TIPOS, default='trazo')
    instruccion_audio = models.TextField(default='Escucha y realiza la actividad.')
    contenido = models.JSONField(default=dict)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('orden', 'id')
        verbose_name = 'actividad'
        verbose_name_plural = 'actividades'

    def __str__(self):
        return f'{self.get_tipo_display()} ({self.leccion.titulo})'


class Alumno(models.Model):
    """Registro histórico del prototipo anterior, sin cuenta de acceso asociada.

    Los nuevos estudiantes se administran mediante User + PerfilUsuario. Se conserva
    este modelo para no borrar los registros antiguos al actualizar el proyecto.
    """
    nombre = models.CharField(max_length=150)
    edad = models.PositiveIntegerField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-fecha_registro',)
        verbose_name = 'registro histórico de alumno'
        verbose_name_plural = 'registros históricos de alumnos'

    def __str__(self):
        return f'{self.nombre} ({self.edad} años)'

    @property
    def categoria_edad(self):
        return 'Adulto' if self.edad >= 18 else 'Menor de edad'
