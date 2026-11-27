# AlfabetizaMX

Plataforma web de apoyo a la lectura y escritura para niñas, niños y personas adultas. Está desarrollada con Python, Django, HTML y CSS. En desarrollo puede usar SQLite; en producción se conecta a PostgreSQL.

## Despliegue en producción

Consulta **[Guía de despliegue en Vercel y Supabase](documentacion/DESPLIEGUE_VERCEL_SUPABASE.md)** para preparar el repositorio, crear la base persistente, configurar secretos, ejecutar migraciones y verificar la aplicación publicada. El repositorio incluye `.gitignore`, `.env.example` y un flujo de pruebas de GitHub Actions.

La aplicación no permite subir archivos de usuarios en esta versión. Sus imágenes, CSS y JavaScript son archivos estáticos versionados en el repositorio y distribuidos por Vercel. No necesita un servicio externo de archivos para sus funciones actuales.

## Requisitos

- Python 3.12 o una versión compatible con Django 6.1.
- Paquetes indicados en `requirements.txt`.

## Instalación en Windows

Abre CMD o PowerShell en la carpeta donde está `manage.py` (la carpeta principal `AlfabetizaMX_Actualizado`) y ejecuta:

```cmd
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py runserver
```

En PowerShell, activa el entorno con `.\.venv\Scripts\Activate.ps1` en lugar del comando de CMD.

Después abre `http://127.0.0.1:8000/`.

## Crear o recuperar el acceso administrador

Si no tienes una cuenta administradora, ejecuta:

```powershell
py manage.py createsuperuser
```

El primer superusuario puede entrar a `/academia/` y gestionar módulos, lecciones, actividades, usuarios y roles. Los grupos Administrador, Tutor y Estudiante se crean automáticamente al ejecutar las migraciones.

## Roles

- **Estudiante:** puede consultar módulos, lecciones y practicar actividades. La cuenta pública siempre se registra como estudiante, ya sea una persona menor o adulta.
- **Tutor:** puede consultar los alumnos que tengan una vinculación activa con su cuenta.
- **Administrador:** puede crear, editar y eliminar módulos, lecciones, actividades y cuentas, además de asignar roles.

Los permisos se validan en el servidor, no solamente ocultando botones de la interfaz.

## Alumnos y cuentas

Los nuevos alumnos se registran mediante una cuenta `User` de Django y un `PerfilUsuario`; la fecha de nacimiento permite distinguir menores de edad y adultos. Para cuentas de menores se solicita confirmar la autorización de madre, padre o tutor.

El modelo `Alumno` anterior se conserva como registro histórico porque no contiene correo, contraseña ni una relación segura con una cuenta. Sus filas se muestran por separado para no borrar ni asociar datos a una persona equivocada.

## Contenido educativo

La migración `0005_crear_10_lecciones_por_modulo` garantiza 10 lecciones por cada uno de los seis apartados iniciales: Vocales, Sílabas, Trazo, Números, Colores y Palabras. Cada lección nueva incluye una actividad de trazo con un objetivo concreto y una instrucción que puede reproducirse en voz. Si una lección ya tenía actividades, la migración las conserva.

El administrador puede seguir agregando, editando o eliminando contenido desde el detalle de cada módulo. El campo de contenido acepta JSON válido. Ejemplo:

```json
{
  "objetivo": "A",
  "letra": "A",
  "imagen_emoji": "🐝",
  "descripcion_visual": "Mira la forma y trázala con calma."
}
```

Los objetivos de escritura admiten letras A-Z y números 0-9, así como palabras de hasta 10 caracteres formadas por ellos.

## Evaluación del trazo y seguimiento

Al terminar una práctica, el navegador envía al servidor los puntos normalizados del dibujo. Django calcula una precisión orientativa comparando el recorrido con plantillas vectoriales sencillas, crea un registro `Intento` y guarda el recorrido en `Trazo`. Se conserva el puntaje, si alcanzó el umbral de práctica, el tiempo y los usos de audio.

La pantalla **Mi progreso** presenta intentos guardados, precisión promedio, minutos de práctica, actividades superadas, avance por módulo y prácticas recientes. Un tutor solo puede consultar el progreso de un estudiante si tiene un vínculo activo. Un administrador puede consultar los registros desde la pantalla de Alumnos.

**Importante:** la puntuación es una guía geométrica de práctica, no un sistema profesional de reconocimiento de escritura ni una evaluación pedagógica definitiva. La forma de escribir cambia entre personas, edades y necesidades motrices; los resultados deben interpretarse con apoyo de un tutor o docente.

## Accesibilidad para personas que están aprendiendo a leer

La interfaz ofrece:

- **Escuchar pantalla:** lee en voz alta el contenido principal en español usando la voz disponible en el navegador.
- **Hablar para navegar:** permite comandos como “abrir vocales”, “abrir sílabas”, “inicio”, “repetir” y “ayuda”, cuando el navegador ofrece reconocimiento de voz y el usuario autoriza el micrófono.
- **Detener voz**, ampliar o reducir el tamaño de la pantalla y activar alto contraste.
- Botones grandes, íconos, instrucciones de audio, modelos visuales y pasos de escuchar, observar y practicar.

La lectura en voz alta utiliza la API de síntesis de voz del navegador. El reconocimiento de voz depende del navegador, del idioma disponible y del permiso de micrófono; siempre quedan disponibles los botones normales como alternativa. Se recomienda probar en una versión actualizada de Chrome o Edge y comprobar que el dispositivo tenga audio.

## Base de datos y actualización

Antes de actualizar un proyecto que ya tiene usuarios o intentos, haz una copia de `db.sqlite3`. Copia los archivos fuente de la actualización, conserva tu archivo `db.sqlite3` y tu carpeta `.venv`, y ejecuta:

```powershell
.\.venv\Scripts\activate
py manage.py migrate
py manage.py check
py manage.py runserver
```

La nueva migración agrega contenido mediante `get_or_create` y no elimina los registros de usuarios, intentos o trazos existentes.

> Este proyecto es un prototipo académico. Antes de usarlo con menores o desplegarlo públicamente, revisa el aviso de privacidad, la autorización de tutores y las medidas de seguridad; cambia `SECRET_KEY`, desactiva `DEBUG` y configura HTTPS.


## Guía visual de trazado

Los ejercicios de escritura muestran puntos verdes numerados para comenzar cada recorrido, una línea animada y una flecha para indicar la dirección. El botón **Ver el recorrido** repite la demostración y la indicación hablada. La guía se reconstruye usando coordenadas normalizadas cuando cambia el tamaño del lienzo. Las actividades sin plantilla vectorial muestran una indicación alternativa.

Para validar los cambios, ejecuta `py manage.py check` y `py manage.py test evaluarme`.


## Rediseño visual 2026

La interfaz incluye navegación lateral adaptable, tarjetas ilustradas para los seis módulos, ruta de aprendizaje, panel de progreso con métricas reales y selector de modo infantil/adulto. Las ilustraciones se guardan en `academia/static/academia/img/`. El diseño conserva los controles de audio, voz y alto contraste.
