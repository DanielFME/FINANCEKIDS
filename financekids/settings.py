# =============================================================================
# ARCHIVO DE CONFIGURACIÓN PRINCIPAL DE DJANGO — settings.py
# =============================================================================
# Este archivo es el "cerebro" de la aplicación.
# Aquí le decimos a Django cómo debe comportarse:
#   - A qué base de datos conectarse
#   - Qué aplicaciones están instaladas
#   - Dónde están los archivos de diseño (CSS, imágenes)
#   - Qué tan segura debe ser la app
#   - Y mucho más
#
# IMPORTANTE: nunca subas contraseñas o claves secretas aquí directamente.
# Todas las cosas sensibles se leen desde "variables de entorno" (explicadas abajo).
# =============================================================================

# --- Librerías que necesitamos importar para que el archivo funcione ---
from pathlib import Path   # Para construir rutas de carpetas de forma segura
import os                  # Para leer variables del sistema operativo
from urllib.parse import urlparse  # Para descomponer una URL en sus partes
from dotenv import load_dotenv     # Para leer el archivo .env con configuraciones locales
import dj_database_url             # Para convertir una URL de base de datos al formato que usa Django

# =============================================================================
# VARIABLES DE ENTORNO
# =============================================================================
# Una "variable de entorno" es una configuración que vive FUERA del código.
# Por ejemplo: la contraseña de la base de datos, la clave secreta, etc.
#
# ¿Por qué usarlas?
# - Seguridad: si subes el código a GitHub, nadie puede ver las contraseñas.
# - Flexibilidad: puedes tener configuraciones diferentes en local y en producción
#   sin cambiar el código.
#
# En tu computador local, estas variables se guardan en el archivo ".env"
# En producción (Render), se configuran en el panel web de Render.
#
# load_dotenv() lee el archivo .env si existe y carga esas variables.
load_dotenv()

# BASE_DIR es la ruta a la carpeta raíz del proyecto (donde está manage.py).
# Se usa para construir rutas a otras carpetas sin escribirlas a mano.
BASE_DIR = Path(__file__).resolve().parent.parent


# =============================================================================
# FUNCIONES AUXILIARES (herramientas internas)
# =============================================================================

def str_to_bool(value, default=False):
    # Convierte un texto como "True", "1", "yes" en el valor booleano True.
    # Esto es necesario porque las variables de entorno siempre son texto,
    # nunca valores reales de Python.
    # Ejemplo: "True" → True, "False" → False, None → default
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def get_env(name, default=None):
    # Lee una variable de entorno por su nombre.
    # Si la variable tiene comillas extras (ej: "mivalor"), las elimina.
    # Si no existe o está vacía, devuelve el valor por defecto.
    value = os.getenv(name)
    if value is None:
        return default

    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        value = value[1:-1].strip()

    return value if value != '' else default


# =============================================================================
# SEGURIDAD
# =============================================================================

# DEBUG: modo de desarrollo o producción.
# - True (desarrollo): Django muestra errores detallados en el navegador.
#   Útil para encontrar bugs mientras programas.
# - False (producción): Django oculta los errores al usuario final por seguridad.
#   Siempre debe ser False cuando la app está publicada en internet.
DEBUG = str_to_bool(get_env('DEBUG'), default=True)

# SECRET_KEY: clave secreta usada por Django para proteger sesiones, formularios,
# contraseñas y otras operaciones de seguridad.
# Es como la "llave maestra" de la app. Nunca debe ser pública.
SECRET_KEY = get_env('SECRET_KEY')

if not SECRET_KEY:
    if DEBUG:
        # En modo desarrollo local, usamos una clave genérica (no importa si es insegura).
        SECRET_KEY = 'django-insecure-dev-key-change-me'
    else:
        # En producción, si no hay SECRET_KEY configurada, la app no arranca.
        # Esto previene que alguien la deje vacía por error en un servidor real.
        raise ValueError('SECRET_KEY no configurada. Define SECRET_KEY en variables de entorno.')

# ALLOWED_HOSTS: lista de dominios desde los que se puede acceder a la app.
# Por ejemplo: "financekids-1-sv9q.onrender.com" o "localhost".
# Esto evita que alguien haga ataques usando un dominio falso.
# Se leen separados por coma desde la variable de entorno ALLOWED_HOSTS.
allowed_hosts_env = get_env('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(',') if host.strip()]

# CSRF_TRUSTED_ORIGINS: dominios que pueden enviar formularios a la app.
# CSRF es un tipo de ataque donde un sitio malicioso intenta enviar datos a
# tu app haciéndose pasar por el usuario. Esta lista define quién sí puede hacerlo.
csrf_trusted_origins_env = get_env('CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in csrf_trusted_origins_env.split(',') if origin.strip()
]


# =============================================================================
# APLICACIONES INSTALADAS
# =============================================================================
# Django divide la app en módulos llamados "apps". Cada uno tiene una función.
# Aquí se registran todas las apps que están activas en el proyecto.
INSTALLED_APPS = [
    'django.contrib.admin',       # Panel de administración (el que ves en /admin/)
    'django.contrib.auth',        # Sistema de usuarios, login y contraseñas
    'django.contrib.contenttypes',# Permite relacionar modelos entre apps
    'django.contrib.sessions',    # Guarda la sesión del usuario (quién está logueado)
    'django.contrib.messages',    # Sistema de mensajes temporales (ej: "Registro exitoso")
    'django.contrib.staticfiles', # Manejo de archivos CSS, imágenes, JavaScript

    'game',  # Nuestra app con los modelos de progreso del usuario (UserProfile)
    'core',  # Nuestra app principal con las vistas, templates y lógica del sitio
]


# =============================================================================
# MIDDLEWARE (capas de procesamiento de cada solicitud)
# =============================================================================
# Cada vez que un usuario visita una página, la solicitud pasa por estos filtros
# en orden. Cada uno cumple una función de seguridad o utilidad.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',           # Seguridad HTTP básica (headers de seguridad)
    'django.contrib.sessions.middleware.SessionMiddleware',    # Manejo de sesiones de usuario
    'django.middleware.common.CommonMiddleware',               # Correcciones comunes (ej: redirigir URLs sin /)
    'django.middleware.csrf.CsrfViewMiddleware',               # Protección contra ataques CSRF en formularios
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Identifica al usuario logueado en cada request
    'django.contrib.messages.middleware.MessageMiddleware',    # Permite enviar mensajes entre vistas
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Evita que la app sea embebida en iframes maliciosos
]

# WhiteNoise: en producción, agrega un middleware especial para servir los archivos
# estáticos (CSS, imágenes) directamente desde Django sin necesitar un servidor
# externo como Nginx. Solo se activa cuando DEBUG=False (producción).
if not DEBUG:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')


# =============================================================================
# URLs Y TEMPLATES
# =============================================================================

# Le dice a Django dónde está el archivo que define las URLs de la app.
ROOT_URLCONF = 'financekids.urls'

# TEMPLATES: configuración de los archivos HTML (plantillas).
# Django busca los templates dentro de cada app en una carpeta llamada "templates".
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Carpeta extra de templates en la raíz (opcional)
        'APP_DIRS': True,  # Busca templates dentro de cada app automáticamente
        'OPTIONS': {
            'context_processors': [
                # Estas funciones agregan datos automáticamente a todos los templates:
                'django.template.context_processors.request',  # La solicitud HTTP actual
                'django.contrib.auth.context_processors.auth',  # El usuario logueado
                'django.contrib.messages.context_processors.messages',  # Mensajes del sistema
            ],
        },
    },
]

# WSGI: el "puente" entre el servidor web (gunicorn en Render) y Django.
# Cuando Render recibe una solicitud, la pasa a Django a través de este módulo.
WSGI_APPLICATION = 'financekids.wsgi.application'


# =============================================================================
# BASE DE DATOS
# =============================================================================
# La base de datos es donde se guardan TODOS los datos persistentes:
# usuarios registrados, su progreso, contraseñas (encriptadas), etc.
#
# Esta sección decide AUTOMÁTICAMENTE a qué base conectarse según las
# variables de entorno disponibles. Orden de prioridad:
#
# 1) USE_SQLITE=True  → SQLite local (archivo en tu computador)
# 2) DATABASE_URL     → PostgreSQL en Render (producción)
# 3) MYSQL_ADDON_*    → MySQL via addon (compatibilidad con otros proveedores)
# 4) DB_*             → MySQL manual (configuración propia)
#
# ¿Dónde viven los datos en producción?
# En Render, la base de datos está en un servicio separado llamado "financekids-db".
# Tu app web (financekids) NO guarda los datos en su propio disco, sino que se
# conecta por internet al servicio PostgreSQL usando la variable DATABASE_URL.
# Esto significa que puedes hacer redeploy de la app sin perder ningún dato.

if str_to_bool(get_env('USE_SQLITE'), default=False):
    # -----------------------------------------------------------------------
    # OPCIÓN 1: SQLite (base de datos local, solo para desarrollo)
    # -----------------------------------------------------------------------
    # SQLite guarda todos los datos en un solo archivo: db.sqlite3
    # Es perfecta para trabajar en tu computador porque no necesita instalación.
    # NO se recomienda para producción porque no soporta múltiples usuarios a la vez.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',  # Ruta del archivo de base de datos
        }
    }

elif get_env('DATABASE_URL'):
    # -----------------------------------------------------------------------
    # OPCIÓN 2: PostgreSQL via DATABASE_URL (producción en Render)
    # -----------------------------------------------------------------------
    # PostgreSQL es una base de datos profesional que soporta muchos usuarios
    # a la vez, es rápida y segura. Es la que usamos en Render.
    #
    # Render inyecta automáticamente la variable DATABASE_URL cuando conectas
    # un servicio PostgreSQL a tu app web. Tiene este formato:
    # postgres://USUARIO:CONTRASEÑA@SERVIDOR:PUERTO/NOMBRE_BASE
    #
    # dj_database_url.config() convierte esa URL al formato que entiende Django.
    #
    # conn_max_age=600: reutiliza conexiones abiertas durante 10 minutos.
    # Esto mejora el rendimiento porque abrir una nueva conexión tiene un costo.
    #
    # ssl_require=not DEBUG: en producción (DEBUG=False) obliga a que la
    # comunicación entre la app y la base de datos viaje encriptada por SSL.
    DATABASES = {
        'default': dj_database_url.config(
            default=get_env('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=not DEBUG,
        )
    }

else:
    # -----------------------------------------------------------------------
    # OPCIÓN 3 y 4: MySQL (compatibilidad con otros entornos)
    # -----------------------------------------------------------------------
    # Este bloque existe para mantener compatibilidad con entornos anteriores
    # del proyecto que usaban MySQL (por ejemplo en Clever Cloud).
    # En Render con PostgreSQL, este bloque normalmente no se ejecuta.
    #
    # Primero intenta leer credenciales de variables MYSQL_ADDON_* (formato addon).
    # Si no las encuentra, intenta con DB_* (formato manual).
    # Si viene una URI completa en MYSQL_ADDON_URI, la descompone para extraer
    # cada parte: usuario, contraseña, servidor, puerto y nombre de la base.
    mysql_addon_uri = get_env('MYSQL_ADDON_URI', '')
    parsed_uri = urlparse(mysql_addon_uri) if mysql_addon_uri else None

    db_name     = get_env('MYSQL_ADDON_DB')       or get_env('DB_NAME')
    db_user     = get_env('MYSQL_ADDON_USER')     or get_env('DB_USER')
    db_password = get_env('MYSQL_ADDON_PASSWORD') or get_env('DB_PASSWORD')
    db_host     = get_env('MYSQL_ADDON_HOST')     or get_env('DB_HOST')
    db_port     = get_env('MYSQL_ADDON_PORT')     or get_env('DB_PORT')

    if parsed_uri:
        # Si viene una URI tipo mysql://user:pass@host:3306/dbname,
        # la usamos para completar cualquier campo que falte.
        db_name     = db_name     or (parsed_uri.path.lstrip('/') if parsed_uri.path else None)
        db_user     = db_user     or parsed_uri.username
        db_password = db_password or parsed_uri.password
        db_host     = db_host     or parsed_uri.hostname
        db_port     = db_port     or (str(parsed_uri.port) if parsed_uri.port else None)

    # Si ninguna variable estaba configurada, usamos valores por defecto
    # para que al menos se pueda levantar en local sin error.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME':     db_name     or 'financekids',
            'USER':     db_user     or 'root',
            'PASSWORD': db_password or '',
            'HOST':     db_host     or 'localhost',
            'PORT':     db_port     or '3306',
        }
    }


# =============================================================================
# VALIDACIÓN DE CONTRASEÑAS
# =============================================================================
# Reglas que debe cumplir una contraseña al registrarse.
# Django las verifica automáticamente cuando un usuario crea su cuenta.
AUTH_PASSWORD_VALIDATORS = [
    # No debe ser muy similar al nombre de usuario o email
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    # Debe tener al menos 8 caracteres
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    # No puede ser una contraseña muy común (ej: "123456", "password")
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    # No puede ser solo números
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =============================================================================
# LOCALIZACIÓN (idioma y zona horaria)
# =============================================================================
LANGUAGE_CODE = 'es-co'              # Idioma: español colombiano
TIME_ZONE     = 'America/Bogota'     # Zona horaria de Colombia (UTC-5)
USE_I18N      = True                 # Activa el sistema de traducción de Django
USE_TZ        = True                 # Guarda todas las fechas con zona horaria (recomendado)


# =============================================================================
# ARCHIVOS ESTÁTICOS (CSS, imágenes, JavaScript)
# =============================================================================
# Los "archivos estáticos" son los que no cambian: hojas de estilo, imágenes, etc.
# Django los maneja de forma especial para servirlos correctamente.

# URL base desde donde se accede a los estáticos en el navegador.
# Ejemplo: /static/css/login.css
STATIC_URL = '/static/'

# Carpetas donde Django busca los archivos estáticos del proyecto.
# En este caso, dentro de la app "core" en la carpeta "static".
STATICFILES_DIRS = [
    BASE_DIR / 'core' / 'static',
]

# Carpeta destino cuando se ejecuta "collectstatic" para producción.
# Django copia todos los estáticos aquí para que WhiteNoise los sirva.
STATIC_ROOT = BASE_DIR / 'staticfiles'

# STORAGES: define cómo se guardan los archivos.
# - 'default': para archivos subidos por usuarios (no aplica en este proyecto aún).
# - 'staticfiles': WhiteNoise comprime y cachea los estáticos para mejor rendimiento
#   en producción. Si un archivo referenciado en un template no existe,
#   el build fallará (esto nos ayuda a detectar errores antes de publicar).
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}


# =============================================================================
# CONFIGURACIONES EXTRA DE SEGURIDAD (solo en producción)
# =============================================================================
# Estas configuraciones solo se activan cuando DEBUG=False (es decir, en Render).
# En local no se aplican para no complicar el desarrollo.
if not DEBUG:
    # Redirige automáticamente todas las visitas HTTP a HTTPS (más seguro).
    SECURE_SSL_REDIRECT = str_to_bool(get_env('SECURE_SSL_REDIRECT'), default=True)

    # La cookie de sesión (que identifica al usuario logueado) solo viaja por HTTPS.
    SESSION_COOKIE_SECURE = True

    # La cookie CSRF (protección de formularios) solo viaja por HTTPS.
    CSRF_COOKIE_SECURE = True

    # HSTS: le dice al navegador que SIEMPRE use HTTPS para este dominio
    # durante el tiempo indicado en segundos (31536000 = 1 año).
    SECURE_HSTS_SECONDS            = int(get_env('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # También aplica a subdominios
    SECURE_HSTS_PRELOAD            = True  # Permite registrar el dominio en la lista HSTS global


# =============================================================================
# LOGIN Y LOGOUT
# =============================================================================
LOGIN_URL           = '/login/'   # Si intentas entrar a una página protegida sin estar logueado,
                                  # Django te redirige aquí automáticamente.
LOGIN_REDIRECT_URL  = '/juego1/'  # Después de iniciar sesión exitosamente, Django redirige aquí.
LOGOUT_REDIRECT_URL = '/'         # Después de cerrar sesión, Django redirige aquí.


# =============================================================================
# CONFIGURACIÓN GENERAL
# =============================================================================
# DEFAULT_AUTO_FIELD: tipo de campo que Django usa por defecto para los IDs
# de cada tabla en la base de datos. BigAutoField soporta números muy grandes.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
