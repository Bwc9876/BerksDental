"""
    This is a collection of configuration data that django reads from We store important data like the secret key and
    the database password in an environment variable These settings are used in production, as it has many settings that
    improve security and performance For example, the DEBUG variable determines many aspects of the website,
    like if /debug_admin/ works. DEBUG is also responsible for showing the error trace pages, which wouldn't be a good
    idea to have for production. We also switch our database from the default sqlite3 file to MySQL, as PythonAnywhere
    provides us a database Finally, we set the STATIC_ROOT and MEDIA_ROOT variables to paths in /var/www/... as this
    allows PythonAnywhere to serve the files
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = False

# Will be changed to the domain we want to host the site on in production
ALLOWED_HOSTS = ['ProductionHost']

INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth',
    'django.contrib.contenttypes', 
    'django.contrib.sessions',
    'django.contrib.messages',
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
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'BerksDentalAssistants.wsgi.application'


# Will be changed to mysql for PythonAnywhere
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

"""
    These settings tell the browser to cache whether the site is secure, and will make the browser redirect to the https
    version of the site, however, if the site isn't secure, the browser will keep redirecting to https anyway, even
    though it has no effect.  So, we'll only enable these settings if we're certain that we can host the site via https
"""

# SECURE_HSTS_SECONDS = 604800
#
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#
# SECURE_HSTS_PRELOAD = True
#
# SECURE_SSL_REDIRECT = True

STATIC_ROOT = '/var/www/BerksDental/static'
STATIC_URL = '/static/'

MEDIA_ROOT = "media/"
MEDIA_URL = "/media/"
