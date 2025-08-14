# settings.py

from pathlib import Path
import os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================================
# CORE SETTINGS
# ==============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
# On Heroku, this is set in your app's "Config Vars"
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-a-very-insecure-default-key')

# SECURITY WARNING: don't run with debug turned on in production!
# On Heroku, DEBUG is automatically set to False.
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# On Heroku, this is set automatically. For local development, it can be empty.
# In your Heroku Config Vars, you should set ALLOWED_HOSTS = your-app-name.herokuapp.com
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost 127.0.0.1').split()


# Application definition
INSTALLED_APPS = [
    'daphne',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'game',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise Middleware should be placed directly after the SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rps.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Use Daphne as the ASGI server
ASGI_APPLICATION = 'rps.asgi.application'


# ==============================================================================
# DATABASE SETTINGS
# ==============================================================================

# This configuration uses the DATABASE_URL from Heroku's environment variables.
# If it doesn't find it, it falls back to the local SQLite database.
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
        ssl_require=True if 'DATABASE_URL' in os.environ else False
    )
}


# ==============================================================================
# PASSWORD AND INTERNATIONALIZATION
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ==============================================================================
# STATIC FILES SETTINGS (for WhiteNoise)
# ==============================================================================

STATIC_URL = 'static/'
# This is where collectstatic will gather all static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
# This tells WhiteNoise to find files in your apps' 'static/' directories
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ==============================================================================
# OTHER SETTINGS
# ==============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'