import os
from pathlib import Path

# === BASE CONFIG ===
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-d6-hxwo53dojql00)t==rs-ftwko*e_ap(7cd(&nt&uq@6@ofl'
DEBUG = True
ALLOWED_HOSTS = ['*']

# === APPLICATIONS ===
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local apps
    'accounts_app',
    'players_app',
    'matches_app',
    'actions_app',
    'gps_app',
    'teams_app',
    'announcements_app',
    'reports_app',
    'tagging_app',
    'goalkeeping_app',
]

# === MIDDLEWARE ===
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'player_statistics_project.urls'

# === TEMPLATES ===
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
                'players_app.context_processors.player_filters',
                'teams_app.context_processors.our_teams_context',
            ],
            'builtins': [
                'django.templatetags.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'player_statistics_project.wsgi.application'

# === DATABASE ===
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# === PASSWORD VALIDATION ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# === INTERNATIONALIZATION ===
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# === STATIC / MEDIA ===

# STATIC FILES
STATIC_URL = '/static/'

# In development: serve from app folders + BASE_DIR/static
STATICFILES_DIRS = [
    BASE_DIR / 'accounts_app' / 'static',
    BASE_DIR / 'players_app' / 'static',
    BASE_DIR / 'matches_app' / 'static',
    BASE_DIR / 'actions_app' / 'static',
    BASE_DIR / 'gps_app' / 'static',
    BASE_DIR / 'teams_app' / 'static',
    BASE_DIR / 'static',
]

# Optional: for collectstatic in staging/production
STATIC_ROOT = '/home/afcportal/public_html/static_player_statistics2/'

# MEDIA FILES
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Optional: for production-like setup
# MEDIA_URL = '/media_player_statistics2/'
# MEDIA_ROOT = '/home/afcportal/public_html/media_player_statistics2/'

# === AUTH ===
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'accounts_app:login'

# === EMAIL (Development only) ===
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# === TIME FORMATS ===
TIME_INPUT_FORMATS = ['%H:%M']

# === DEFAULT FIELD TYPE ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
