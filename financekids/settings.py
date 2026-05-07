from pathlib import Path
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
import dj_database_url

# Cargar variables del archivo .env (si existe)
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def str_to_bool(value, default=False):
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def get_env(name, default=None):
    value = os.getenv(name)
    if value is None:
        return default

    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        value = value[1:-1].strip()

    return value if value != '' else default

# ------------------------
# SEGURIDAD
# ------------------------
DEBUG = str_to_bool(get_env('DEBUG'), default=True)
SECRET_KEY = get_env('SECRET_KEY')

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-dev-key-change-me'
    else:
        raise ValueError('SECRET_KEY no configurada. Define SECRET_KEY en variables de entorno.')

# Hosts permitidos separados por coma: ejemplo "miapp.com,.onrender.com"
allowed_hosts_env = get_env('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(',') if host.strip()]

csrf_trusted_origins_env = get_env('CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in csrf_trusted_origins_env.split(',') if origin.strip()
]

# ------------------------
# APLICACIONES
# ------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    

    'game',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if not DEBUG:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

ROOT_URLCONF = 'financekids.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # por si usas plantillas personalizadas
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'financekids.wsgi.application'

# ------------------------
# BASE DE DATOS
# ------------------------
# Prioridad: 1) USE_SQLITE=True (local sin BD)  2) DATABASE_URL (Render)
#            3) MYSQL_ADDON_* (Clever Cloud)     4) DB_* (MySQL local)
if str_to_bool(get_env('USE_SQLITE'), default=False):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
elif get_env('DATABASE_URL'):
    # Render inyecta DATABASE_URL apuntando a PostgreSQL automaticamente.
    DATABASES = {
        'default': dj_database_url.config(
            default=get_env('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=not DEBUG,
        )
    }
else:
    mysql_addon_uri = get_env('MYSQL_ADDON_URI', '')
    parsed_uri = urlparse(mysql_addon_uri) if mysql_addon_uri else None

    db_name = get_env('MYSQL_ADDON_DB') or get_env('DB_NAME')
    db_user = get_env('MYSQL_ADDON_USER') or get_env('DB_USER')
    db_password = get_env('MYSQL_ADDON_PASSWORD') or get_env('DB_PASSWORD')
    db_host = get_env('MYSQL_ADDON_HOST') or get_env('DB_HOST')
    db_port = get_env('MYSQL_ADDON_PORT') or get_env('DB_PORT')

    if parsed_uri:
        db_name = db_name or (parsed_uri.path.lstrip('/') if parsed_uri.path else None)
        db_user = db_user or parsed_uri.username
        db_password = db_password or parsed_uri.password
        db_host = db_host or parsed_uri.hostname
        db_port = db_port or (str(parsed_uri.port) if parsed_uri.port else None)

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': db_name or 'financekids',
            'USER': db_user or 'root',
            'PASSWORD': db_password or '',
            'HOST': db_host or 'localhost',
            'PORT': db_port or '3306',
        }
    }
# ------------------------
# VALIDACIÓN DE CONTRASEÑAS
# ------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ------------------------
# LOCALIZACIÓN
# ------------------------
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# ------------------------
# ARCHIVOS ESTÁTICOS
# ------------------------
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'core' / 'static',  # esta es la ruta real en tu sistema de archivos
]

STATIC_ROOT = BASE_DIR / 'staticfiles'
# STATICFILES_STORAGE fue deprecado en Django 4.2; se usa STORAGES
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}


if not DEBUG:
    SECURE_SSL_REDIRECT = str_to_bool(get_env('SECURE_SSL_REDIRECT'), default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(get_env('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True



# ------------------------
# LOGIN / LOGOUT
# ------------------------
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/juego1/'
LOGOUT_REDIRECT_URL = '/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
