from settings import *

#SITE_ID = 3

MIDDLEWARE_CLASSES += (
        'django.middleware.csrf.CsrfViewMiddleware',
        'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS +=(
        'debug_toolbar',
)

INTERNAL_IPS = ('127.0.0.1',
                '192.168.1.2',)

DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS':False,
}

DATABASES = {
    'default': {
#        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '/tmp/nyu11',                      # Database name or path to database file if using sqlite3.
#        'USER': 'postgres',                 # Not used with sqlite3.
#        'PASSWORD': 'postgres',             # Not used with sqlite3.
        'HOST': 'localhost',                # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                         # Set to empty string for default. Not used with sqlite3.
    }
}


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'django.develop@gmail.com'
EMAIL_HOST_PASSWORD = 'kfhjkbybot'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'no-reply@nyu.com'

# This next few lines should be in the end of settings file!
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console': {
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            #'filters': ['special']
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'annotation_server.log',
            'formatter': 'verbose',
        },
        'django_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'django.log'
        },

    },
    'loggers': {
        'django': {
            'handlers':['django_file'],
            #'propagate': True,
            'level':'INFO',
        },
        'api': {
            'handlers': ['console', 'file'],
            'propagate': False,
            'level': 'INFO'
        }
    }
}

#DEFAULT_CHARSET = ""
