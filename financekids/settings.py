from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def str_to_bool(value, default=False):
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def env_get(env, name, default=None):
    value = env.get(name)
    if value is None:
        return default

    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        value = value[1:-1].strip()

    return value if value != '' else default


def get_env(name, default=None):
    return env_get(os.environ, name, default)


def is_postgres_url(database_url):
    return database_url.startswith(('postgres://', 'postgresql://'))


def parse_database_url(database_url, debug=False):
    return dj_database_url.parse(
        database_url,
        conn_max_age=600,
        ssl_require=is_postgres_url(database_url) and not debug,
    )


def build_mysql_database_config(env, debug=False):
    mysql_url = env_get(env, 'MYSQL_URL') or env_get(env, 'MYSQL_ADDON_URI', '')
    if mysql_url:
        config = parse_database_url(mysql_url, debug=debug)
    else:
        config = {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'financekids',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '3306',
        }

    db_name = (
        env_get(env, 'MYSQLDATABASE')
        or env_get(env, 'MYSQL_ADDON_DB')
        or env_get(env, 'DB_NAME')
    )
    db_user = (
        env_get(env, 'MYSQLUSER')
        or env_get(env, 'MYSQL_ADDON_USER')
        or env_get(env, 'DB_USER')
    )
    db_password = (
        env_get(env, 'MYSQLPASSWORD')
        or env_get(env, 'MYSQL_ADDON_PASSWORD')
        or env_get(env, 'DB_PASSWORD')
    )
    db_host = (
        env_get(env, 'MYSQLHOST')
        or env_get(env, 'MYSQL_ADDON_HOST')
        or env_get(env, 'DB_HOST')
    )
    db_port = (
        env_get(env, 'MYSQLPORT')
        or env_get(env, 'MYSQL_ADDON_PORT')
        or env_get(env, 'DB_PORT')
    )

    config['NAME'] = db_name or config.get('NAME') or 'financekids'
    config['USER'] = db_user or config.get('USER') or 'root'
    config['PASSWORD'] = db_password or config.get('PASSWORD') or ''
    config['HOST'] = db_host or config.get('HOST') or 'localhost'
    config['PORT'] = db_port or config.get('PORT') or '3306'

    return config


def build_default_database_config(env=None, debug=False, base_dir=None):
    if env is None:
        env = os.environ
    if base_dir is None:
        base_dir = BASE_DIR

    if str_to_bool(env_get(env, 'USE_SQLITE')):
        return {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': base_dir / 'db.sqlite3',
        }

    database_url = env_get(env, 'DATABASE_URL')
    if database_url:
        return parse_database_url(database_url, debug=debug)

    return build_mysql_database_config(env, debug=debug)


# default=False: si olvidas definir DEBUG en producción, falla de forma segura.
DEBUG = str_to_bool(get_env('DEBUG'), default=False)

SECRET_KEY = get_env('SECRET_KEY')

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-dev-key-change-me'
    else:
        raise ValueError('SECRET_KEY no configurada. Define SECRET_KEY en variables de entorno.')

allowed_hosts_env = get_env('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(',') if host.strip()]

csrf_trusted_origins_env = get_env('CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in csrf_trusted_origins_env.split(',') if origin.strip()
]

# Railway inyecta RAILWAY_PUBLIC_DOMAIN automáticamente con el dominio público de la app.
railway_public_domain = get_env('RAILWAY_PUBLIC_DOMAIN')
if railway_public_domain:
    if railway_public_domain not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(railway_public_domain)
    railway_origin = f'https://{railway_public_domain}'
    if railway_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(railway_origin)

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
        'DIRS': [BASE_DIR / 'templates'],
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

DATABASES = {
    'default': build_default_database_config(debug=DEBUG)
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'core' / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': (
            'whitenoise.storage.CompressedManifestStaticFilesStorage'
            if not DEBUG else
            'django.contrib.staticfiles.storage.StaticFilesStorage'
        ),
    },
}

if not DEBUG:
    # Railway/Render terminan el TLS en el proxy y reenvían la petición como HTTP
    # interno con el header X-Forwarded-Proto; sin esto, SECURE_SSL_REDIRECT provoca
    # un bucle infinito de redirects (ERR_TOO_MANY_REDIRECTS).
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = str_to_bool(get_env('SECURE_SSL_REDIRECT'), default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(get_env('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/juego1/'
LOGOUT_REDIRECT_URL = '/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
