"""
Django project settings
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# This will set the SECRET_KEY to "no_secret", unless the SECRET_KEY
# environment variable is set.
#
# While this static-django-bootstrap app is only being used as intended -
# to serve essentially static templates with no dynamic functionality,
# an insecure SECRET_KEY won't introduce any insecurities in the application.
#
# However, as soon as you start using sessions, passwords, crypto functions
# or anything that uses django.utils.crypt.get_random_string(),
# you will need a strong SECRET_KEY to ensure your app remains secure
# (see: http://stackoverflow.com/a/15383766/613540)
#
# At this point you should ensure the SECRET_KEY environment variable is set
# in the Production deployment with a secure key, e.g. from
# http://www.miniwebtool.com/django-secret-key-generator/
SECRET_KEY = os.environ.get('SECRET_KEY', 'no_secret')

# See https://docs.djangoproject.com/en/dev/ref/contrib/
INSTALLED_APPS = [
    'canonicalwebteam',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'webapp',
]

ALLOWED_HOSTS = ['*']

MIDDLEWARE_CLASSES = []

DEBUG = os.environ.get('DJANGO_DEBUG', 'false').lower() == 'true'
ROOT_URLCONF = 'webapp.urls'
WSGI_APPLICATION = 'webapp.wsgi.application'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = False
USE_TZ = False
STATIC_ROOT = 'static'
STATIC_URL = '/static/'
STATICFILES_FINDERS = ['django_static_root_finder.StaticRootFinder']
ASSET_SERVER_URL = 'https://assets.ubuntu.com/v1/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'builtins': [
                'webapp.templatetags.feeds',
                'webapp.templatetags.utils',
            ],
            'context_processors': [
                'django_asset_server_url.asset_server_url',
            ],
        },
    },
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'error_file': {
            'level': 'ERROR',
            'filename': os.path.join(BASE_DIR, 'django-error.log'),
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1 * 1024 * 1024,
            'backupCount': 2
        }
    },
    'loggers': {
        'django': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': True
        }
    }
}
