"""
Django settings for player_statistics_project.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Security ---
SECRET_KEY = 'django-insecure-d6-hxwo53dojql00)t==rs-ftwko*e_ap(7cd(&nt&uq@6@ofl'
DEBUG = True  # Set False in production
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'azamfcportal.com']

# --- Installed Apps ---
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
    'defensive_app',
    'lineup_app',
    'perfomance_rating_app',
    'training_app',
]

# --- Middleware ---
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

# --- Templates ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'players_app.context_processors.player_filters',
                'teams_app.context_processors.our_teams_context',
            ],
            'builtins': ['django.templatetags.static'],
        },
    },
]

WSGI_APPLICATION = 'player_statistics_project.wsgi.application'

# --- Database ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- Password Validation ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Internationalization ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- Static & Media Configuration (Flexible Mode) ---
if DEBUG:
    # Development Mode
    STATIC_URL = '/static/'
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'accounts_app', 'static'),
        os.path.join(BASE_DIR, 'actions_app', 'static'),
        os.path.join(BASE_DIR, 'goalkeeping_app', 'static'),
        os.path.join(BASE_DIR, 'gps_app', 'static'),
        os.path.join(BASE_DIR, 'matches_app', 'static'),
        os.path.join(BASE_DIR, 'players_app', 'static'),
        os.path.join(BASE_DIR, 'reports_app', 'static'),
        os.path.join(BASE_DIR, 'tagging_app', 'static'),
        os.path.join(BASE_DIR, 'teams_app', 'static'),
        os.path.join(BASE_DIR, 'static'),
    ]
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
else:
    # Production Mode
    STATIC_URL = '/static_player_statistics2/'
    STATIC_ROOT = '/home/afcportal/public_html/static_player_statistics2'
    MEDIA_URL = '/media_player_statistics2/'
    MEDIA_ROOT = '/home/afcportal/public_html/media_player_statistics2'

# --- Authentication Redirects ---
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'accounts_app:login'

# --- Email (development) ---
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# --- Time Formats ---
TIME_INPUT_FORMATS = ['%H:%M']

# --- Default Primary Key ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
