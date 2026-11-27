# Despliegue de AlfabetizaMX en Vercel y Supabase

## Estado de esta entrega

Este repositorio está preparado para conectarse a Vercel y PostgreSQL. **La publicación, la creación de la base de datos y las migraciones remotas requieren las cuentas de su propietario; no se realizan automáticamente al extraer el ZIP.** No debe afirmarse que existe una URL productiva hasta comprobarla realmente.

## 1 Arquitectura

- **Cliente:** HTML, CSS y JavaScript generados y servidos por las plantillas Django.
- **Aplicación:** Django 6.1.1, ejecutado como función Python en Vercel.
- **Persistencia:** PostgreSQL en Supabase mediante el ORM de Django. SQLite solo es una alternativa de desarrollo local.
- **Estáticos:** `academia/static/`, recopilados con `collectstatic` y servidos por la CDN de Vercel.
- **Archivos de usuario:** esta versión no contiene campos `FileField` o `ImageField` ni flujos de carga de archivos. Por ello, no se requiere Storage, S3 o FS adicional por ahora.

## 2 Preparar y revisar el repositorio

1. Crea un repositorio GitHub privado o público para el código, sin archivos de datos ni credenciales.
2. Sube el **contenido** de la carpeta `AlfabetizaMX_Produccion` a la raíz del repositorio; en la raíz deben quedar `manage.py`, `requirements.txt` y la carpeta `miweb`.
3. Comprueba que `.venv`, `db.sqlite3`, `.env`, `staticfiles`, `__pycache__` y `.vercel` no estén incluidos. `.env.example` solo contiene nombres y valores de ejemplo.
4. Configura en GitHub la rama `main` y comprueba el resultado de **Pruebas Django** en Actions. No incluyas `DATABASE_URL` real ni contraseñas en commits, capturas o logs.

## 3 Crear la base persistente en Supabase

1. En https://supabase.com crea un proyecto PostgreSQL; conserva su contraseña **solo en un gestor de contraseñas**.
2. En el panel, abre **Connect**. Para la aplicación serverless de Vercel copia la cadena **Transaction pooler**, que suele utilizar el puerto `6543` (verifica host y usuario en tu propio panel; nunca los inventes).
3. Configura esa cadena como `DATABASE_URL` de tipo **Secret** en Vercel. La aplicación fuerza SSL y desactiva consultas preparadas, compatibles con el pooler transaccional.
4. Para ejecutar las migraciones iniciales desde tu equipo, utiliza una conexión directa si tu red admite IPv6; en caso contrario, utiliza la **Session pooler**, normalmente en puerto `5432`. No es necesario usar la URL de transacción para las migraciones.
5. Antes de migrar datos reales desde SQLite, realiza una copia de seguridad local y estudia cómo transferir usuarios, claves y avances. Este ZIP no incluye `db.sqlite3`, por lo que una base nueva se inicializa sin las cuentas anteriores.

**Importante:** `migrate` no debe ejecutarse en cada petición de Vercel ni asumirse como parte automática del despliegue. Se ejecuta de forma controlada antes de usar el sitio público.

## 4 Preparar el entorno local para migrar

En Windows PowerShell, desde la carpeta que contiene `manage.py`:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py check
python manage.py test
```

Para migrar PostgreSQL, define **en tu sesión privada** las variables `DATABASE_URL`, `DJANGO_SECRET_KEY` y `DJANGO_ENV=production`. No guardes sus valores en scripts versionados ni en capturas. Utiliza la URL de conexión adecuada para migraciones y ejecuta:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py check --deploy
```

Una vez finalizadas las migraciones y creado el administrador, limpia las variables sensibles de la sesión que ya no necesites. El superusuario se crea en PostgreSQL, no en el SQLite local.

## 5 Conectar GitHub a Vercel

1. En https://vercel.com elige **Add New > Project** e importa el repositorio.
2. Mantén el directorio raíz donde está `manage.py`. Vercel identifica aplicaciones Django y lee `requirements.txt`; no necesita un archivo `vercel.json` con redirecciones antiguas.
3. Antes de desplegar, agrega en el entorno **Production**:

| Variable | Tipo | Uso |
| --- | --- | --- |
| `DATABASE_URL` | Secret | Cadena del Transaction pooler de PostgreSQL |
| `DJANGO_SECRET_KEY` | Secret | Clave aleatoria y privada de Django |
| `DJANGO_ENV` | Config | `production` |
| `DJANGO_ALLOWED_HOSTS` | Config | Dominio real del sitio, sin `https://` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Config | URL `https://` completa del sitio |

4. No necesitas configurar manualmente `VERCEL` ni `VERCEL_URL`: Vercel los facilita durante el despliegue. El código admite el dominio dinámico de Vercel y los dominios adicionales incluidos en `DJANGO_ALLOWED_HOSTS`.
5. Pulsa **Deploy** y consulta logs. Al finalizar, verifica que abre la ruta `/academia/` y que los recursos estáticos cargan sin errores.
6. Si después cambias alguna variable, realiza **Redeploy** para aplicar el valor nuevo.

No se deben colocar estos secretos en variables públicas del navegador, código JavaScript, HTML, `README.md` o imágenes de evidencia.

## 6 Validaciones de aceptación

1. Abrir la URL del deployment por HTTPS y comprobar que `/` redirige a `/academia/`.
2. Verificar CSS, iconos y fotografías de módulos; ninguno debe devolver 404.
3. Registrar una **cuenta de prueba ficticia**, cerrar sesión y volver a entrar.
4. Completar una actividad de trazo, guardar el intento y consultar **Mi progreso**.
5. Recargar la página y repetir el acceso desde otro navegador: los datos deben seguir presentes en PostgreSQL.
6. Acceder con usuario estudiante a vistas administrativas y verificar que no obtiene permisos indebidos.
7. Revisar Vercel Logs y Supabase Database para confirmar ausencia de errores de aplicación o conexión.
8. Guardar evidencias con fecha, URL pública, commit de GitHub, estado de pruebas y resultados; ocultar toda información sensible.

## 7 Seguridad y privacidad

En despliegue se fuerza `DEBUG=False`, se exige clave secreta y base persistente, se verifica `ALLOWED_HOSTS`, se habilitan cookies seguras, redirección HTTPS, cabecera del proxy y HSTS. Django mantiene la protección CSRF y validadores de contraseña. Deben rotarse las claves que alguna vez se hayan compartido.

La aplicación actual no envía correos transaccionales. En producción se utiliza la clase SMTP (no la consola de desarrollo), pero **no habrá envío real** hasta configurar opcionalmente `DJANGO_SMTP_HOST`, `DJANGO_SMTP_PORT`, `DJANGO_SMTP_USER`, `DJANGO_SMTP_PASSWORD` (Secret) y `DJANGO_SMTP_USE_TLS`. No es necesario agregar SMTP para las pruebas educativas existentes. Los avisos `security.W005` y `security.W021` de `check --deploy` pueden mantenerse mientras no se haya verificado que todos los subdominios estén bajo HTTPS ni preparado la inclusión HSTS preload.

Al tratarse de una plataforma educativa que puede almacenar información de menores, **antes de usar datos reales de estudiantes** se debe completar una revisión de aviso de privacidad, autorización verificable de responsables, mínima recolección de datos, acceso por roles y política de eliminación. Para evaluación académica, usar cuentas ficticias.

## 8 Evidencias y reporte técnico

Incluye capturas de: estructura del repositorio, prueba de GitHub Actions, configuración de Vercel con **valores ocultos**, URL HTTPS, panel de Supabase sin credenciales, migraciones exitosas, pruebas de registro y seguimiento, y persistencia después de reiniciar sesión.

El reporte técnico final solo debe afirmar **"desplegado y verificado"** después de comprobar la URL real. Hasta entonces, el estado correcto es **"código preparado para despliegue"**.

## Referencias técnicas

- Vercel Django: https://vercel.com/changelog/zero-configuration-django-support
- Vercel Python Runtime: https://vercel.com/docs/functions/runtimes/python
- Supabase PostgreSQL: https://supabase.com/docs/guides/database/connecting-to-postgres
- Vercel Secrets: https://vercel.com/docs/environment-variables
- Django deployment checklist: https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/
