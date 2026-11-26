from datetime import date

from django.contrib.auth.models import User, Group
from django.test import TestCase
from django.urls import reverse

from alfabetizacion.models import PerfilUsuario
from .models import Actividad, Leccion, Modulo


class AccesoYPermisosTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin_prueba', email='admin@example.com', password='ClaveSegura123!'
        )
        self.estudiante = User.objects.create_user(
            username='alumno_prueba', email='alumno@example.com', password='ClaveSegura123!'
        )
        self.modulo = Modulo.objects.create(nombre='Vocales', orden=1)

    def test_inicio_redirige_a_login_si_no_hay_sesion(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_estudiante_puede_ver_modulo(self):
        self.client.login(username='alumno_prueba', password='ClaveSegura123!')
        response = self.client.get(reverse('detalle_modulo', args=[self.modulo.pk]))
        self.assertEqual(response.status_code, 200)

    def test_estudiante_no_puede_crear_modulo(self):
        self.client.login(username='alumno_prueba', password='ClaveSegura123!')
        response = self.client.get(reverse('crear_modulo'))
        self.assertEqual(response.status_code, 403)

    def test_administrador_puede_crear_modulo(self):
        self.client.login(username='admin_prueba', password='ClaveSegura123!')
        response = self.client.post(reverse('crear_modulo'), {'nombre': 'Sílabas', 'orden': 2})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Modulo.objects.filter(nombre='Sílabas').exists())

    def test_admin_puede_crear_leccion_y_actividad(self):
        self.client.login(username='admin_prueba', password='ClaveSegura123!')
        response = self.client.post(reverse('crear_leccion'), {
            'modulo': self.modulo.pk, 'titulo': 'Lección de prueba', 'nivel': 1, 'orden': 1,
        })
        self.assertEqual(response.status_code, 302)
        leccion = Leccion.objects.get(modulo=self.modulo, titulo='Lección de prueba')
        response = self.client.post(reverse('crear_actividad'), {
            'leccion': leccion.pk, 'tipo': 'trazo',
            'instruccion_audio': 'Traza la letra A.', 'contenido': '{"letra":"A"}', 'orden': 1,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Actividad.objects.filter(leccion=leccion).exists())

    def test_admin_puede_consultar_usuarios_y_alumnos(self):
        self.client.login(username='admin_prueba', password='ClaveSegura123!')
        self.assertEqual(self.client.get(reverse('gestion_usuarios')).status_code, 200)
        self.assertEqual(self.client.get(reverse('lista_alumnos')).status_code, 200)

    def test_usuario_normal_no_puede_consultar_usuarios(self):
        self.client.login(username='alumno_prueba', password='ClaveSegura123!')
        self.assertEqual(self.client.get(reverse('gestion_usuarios')).status_code, 403)

    def test_administrador_puede_crear_tutor(self):
        self.client.login(username='admin_prueba', password='ClaveSegura123!')
        response = self.client.post(reverse('crear_usuario'), {
            'username': 'tutora_prueba', 'first_name': 'María', 'last_name': 'Tutor',
            'email': 'tutora@example.com', 'rol': 'tutor',
            'fecha_nacimiento': '1990-01-01',
            'password1': 'UnaClaveFuerte2026!', 'password2': 'UnaClaveFuerte2026!',
        })
        self.assertEqual(response.status_code, 302)
        tutor = User.objects.get(username='tutora_prueba')
        self.assertEqual(tutor.perfil.rol, PerfilUsuario.ROL_TUTOR)
        self.assertTrue(tutor.groups.filter(name='Tutor').exists())

    def test_estudiante_no_puede_eliminar_modulo(self):
        self.client.login(username='alumno_prueba', password='ClaveSegura123!')
        response = self.client.post(reverse('eliminar_modulo', args=[self.modulo.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Modulo.objects.filter(pk=self.modulo.pk).exists())

    def test_usuario_con_rol_administrador_tiene_permisos(self):
        operador = User.objects.create_user(
            username='operador', email='operador@example.com', password='ClaveSegura123!'
        )
        operador.perfil.rol = PerfilUsuario.ROL_ADMIN
        operador.perfil.save()
        grupo = Group.objects.get(name='Administrador')
        operador.groups.set([grupo])
        self.client.login(username='operador', password='ClaveSegura123!')
        response = self.client.get(reverse('crear_modulo'))
        self.assertEqual(response.status_code, 200)


class RegistroEstudianteTests(TestCase):
    def test_registro_crea_usuario_y_perfil_estudiante(self):
        response = self.client.post(reverse('registro'), {
            'username': 'lectora',
            'first_name': 'Ana',
            'last_name': 'Prueba',
            'email': 'ana@example.com',
            'fecha_nacimiento': '2000-05-10',
            'password1': 'UnaClaveFuerte2026!',
            'password2': 'UnaClaveFuerte2026!',
            'acepto_aviso_privacidad': 'on',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='lectora')
        self.assertEqual(user.perfil.rol, PerfilUsuario.ROL_ESTUDIANTE)
        self.assertTrue(user.perfil.acepto_aviso_privacidad)
        self.assertTrue(user.groups.filter(name='Estudiante').exists())

    def test_registro_menor_requiere_autorizacion(self):
        response = self.client.post(reverse('registro'), {
            'username': 'menor',
            'first_name': 'Luis',
            'last_name': 'Prueba',
            'email': 'luis@example.com',
            'fecha_nacimiento': '2017-05-10',
            'password1': 'UnaClaveFuerte2026!',
            'password2': 'UnaClaveFuerte2026!',
            'acepto_aviso_privacidad': 'on',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='menor').exists())


class AccesibilidadPantallasTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(
            username='practicante', email='practicante@example.com', password='ClaveSegura123!'
        )
        self.modulo = Modulo.objects.create(nombre='Vocales', orden=1)
        self.leccion = Leccion.objects.create(
            modulo=self.modulo, titulo='Conociendo la A', nivel=1, orden=1
        )
        self.actividad = Actividad.objects.create(
            leccion=self.leccion, tipo='trazo',
            instruccion_audio='Escucha y traza la letra A.',
            contenido={'letra': 'A'}, orden=1,
        )
        self.client.login(username='practicante', password='ClaveSegura123!')

    def test_inicio_incluye_ayudas_de_voz_y_guia_visual(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Escuchar el contenido de esta pantalla')
        self.assertContains(response, 'icono-escuchar.png')
        self.assertContains(response, 'Escuchar información del módulo Vocales')

    def test_modulo_incluye_audio_para_leccion_y_actividad(self):
        response = self.client.get(reverse('detalle_modulo', args=[self.modulo.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Escuchar la lección Conociendo la A')
        self.assertContains(response, 'Escuchar guía del módulo')
        self.assertContains(response, 'Comenzar')

    def test_actividad_muestra_guia_visual_y_botones_grandes(self):
        response = self.client.get(reverse('realizar_actividad', args=[self.actividad.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Escuchar la instrucción del ejercicio')
        self.assertContains(response, 'id="targetText"')
        self.assertContains(response, 'Terminé')
        self.assertContains(response, 'drawingCanvas')


class CatalogoInicialTests(TestCase):
    def test_los_seis_apartados_tienen_diez_lecciones_con_actividad(self):
        for nombre in ('Vocales', 'Sílabas', 'Trazo', 'Números', 'Colores', 'Palabras'):
            with self.subTest(modulo=nombre):
                modulo = Modulo.objects.get(nombre=nombre)
                self.assertEqual(modulo.lecciones.count(), 10)
                self.assertEqual(
                    modulo.lecciones.filter(actividades__isnull=False).distinct().count(),
                    10,
                )
