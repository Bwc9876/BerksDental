"""
    This is a collection of configuration data that django reads from
    We store important data like the secret key in an environment variable
    These settings should be used for debugging only, in production we use production.py
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "a^0$j#*i7x-0=zpg1=vmti*9zhh2i!oi$kx$#bq&7)1jvl%ne&3z"

DEBUG = True

ALLOWED_HOSTS = ['berksdental.benjamincrocker.repl.co', '127.0.0.1', 'localhost', '192.168.86.29', '71.225.44.187']

INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django_password_validators',
    'django_password_validators.password_history',
    'main',
    'edit'
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

ROOT_URLCONF = 'BerksDentalAssistants.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'main.contexts.base_data',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'BerksDentalAssistants.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = "edit.User"

AUTH_PASSWORD_VALIDATORS = [{
    'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
}, {
    'NAME':
        'django_password_validators.password_history.password_validation.UniquePasswordsValidator',
}, {
    'NAME':
        'edit.validators.RequiredCharactersValidator'
}]

LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "/admin/"
LOGOUT_REDIRECT_URL = "/admin/login/?alert=You Have Been Logged Out&alertType=info"

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_ROOT = "media/"
MEDIA_URL = "/media/"
