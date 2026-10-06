"""
Django settings for sysuniversidad project.
Sistema Web de Gestión Académica Universitaria con Análisis de Datos y Predicción de Riesgo Académico.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno desde .env
load_dotenv(BASE_DIR / '.env')

# Clave secreta y modo depuración
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-sysuniversidad-academic-ml-platform-2026')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',') if host.strip()]

# Definición de Aplicaciones del Sistema
INSTALLED_APPS = [
    # Django Core Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Módulos del Sistema Universitario
    'cuentas.apps.CuentasConfig',
    'academico.apps.AcademicoConfig',
    'matriculas.apps.MatriculasConfig',
    'asistencia.apps.AsistenciaConfig',
    'calificaciones.apps.CalificacionesConfig',
    'analitica.apps.AnaliticaConfig',
    'predicciones.apps.PrediccionesConfig',
    'reportes.apps.ReportesConfig',
    # Módulos complementarios (del dump SQL)
    'seguridad.apps.SeguridadConfig',
    'infraestructura.apps.InfraestructuraConfig',
    'admision.apps.AdmisionConfig',
    'finanzas.apps.FinanzasConfig',
    'tramites.apps.TramitesConfig',
    'egresados.apps.EgresadosConfig',
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

ROOT_URLCONF = 'core.urls'

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
                'cuentas.context_processors.usuario_contexto',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Configuración de Base de Datos (Soporte Dual MariaDB/MySQL y SQLite)
DB_ENGINE_CHOICE = os.getenv('DB_ENGINE', 'sqlite').lower()

if DB_ENGINE_CHOICE == 'mysql':
    import pymysql
    pymysql.install_as_MySQLdb()
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'sysuniversidad_db'),
            'USER': os.getenv('DB_USER', 'root'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', '127.0.0.1'),
            'PORT': os.getenv('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            }
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Modelo de Usuario Personalizado
AUTH_USER_MODEL = 'cuentas.Usuario'

# Validadores de Contraseña
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internacionalización y Localización (Perú)
LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'es-pe')
TIME_ZONE = os.getenv('TIME_ZONE', 'America/Lima')
USE_I18N = True
USE_TZ = True

# Archivos Estáticos y Medios
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redirecciones de Autenticación
LOGIN_URL = 'cuentas:login'
LOGIN_REDIRECT_URL = 'cuentas:dashboard'
LOGOUT_REDIRECT_URL = 'cuentas:login'

# Directorio de modelos ML serializados
ML_MODELS_DIR = BASE_DIR / 'ml_models'
ML_MODELS_DIR.mkdir(parents=True, exist_ok=True)
