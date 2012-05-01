# Django settings for server project.
import os
import sys

TEST = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

PROJECT_ROOT =  os.path.abspath(os.path.dirname(__file__))


ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS
'''
 Here you should to setup DB access parameters.
 You can use MySQL, Postrges, SQLite3 or Oracle.
 Choose one of the engines listed in ENGINE comments.
 Then setup DB name, username and password to access DB.
 If DB is not on the local host you should to setup HOST and PORT.

           ======== Example ==========
 For example you have:
   MySQL DB named                                      annotations
   username to access this DB is                       annotation_servc_user
   password                                            Annotations_11
   host where is located DB is                         192.168.1.2
   port on this host to access MySQL DB is             3310
       but if you don't know which port to use try don't set this option. In this case
       annotation service will try to connect to the DB with default port for this DB.

 So, you need to write this:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'annotations',
        'USER': 'annotation_servc_user',
        'PASSWORD': 'Annotations_11',
        'HOST': '192.168.1.2',
        'PORT': '3310',
    }
}

Please read comments below for correct setting up DB access.
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Database name or path to database file if using sqlite3.
        'USER': '',                 # Not used with sqlite3.
        'PASSWORD': '',             # Not used with sqlite3.
        'HOST': '',                # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                         # Set to empty string for default. Not used with sqlite3.
    },
}

if 'test' in sys.argv:
    #print "REPLACE DB NAME"
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True
# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')


# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ph-g94ur3=j=^btgag7w-!92*)z409gk!_xv(r&o!(yq8kd(8r'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'api.middleware.ContentTypeMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",

    "profile.context_processors.current_site",

#    "django.contrib.messages.context_processors.messages"

    )

ROOT_URLCONF = 'annotation_server.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)
AUTHENTICATION_BACKENDS = (
    'api.auth_backends.CustomUserModelBackend',
    'django.contrib.auth.backends.ModelBackend',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',

    'django.contrib.admin',

    'piston',
    'south',
    'django_nose',
    'registration',
    'django.contrib.markup',
    'django_extensions',
    #'tastypie',
    #'social_auth',
    'django.contrib.webdesign',

    'api',
    'profile',
)

LOGIN_REDIRECT_URL = '/nginx/annotations/'

AUTH_USER_EMAIL_UNIQUE = True

SKIP_SOUTH_TESTS=True
SOUTH_TESTS_MIGRATE = False
######
# Email settings

#SERVER_EMAIL = 'no-reply@intvideo.tv'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'your_nickname@gmail.com'
EMAIL_HOST_PASSWORD = 'password'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'no-reply@nyu.com'
#######

ACCOUNT_ACTIVATION_DAYS = 2 #

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_PLUGINS = ['nose.plugins.cover.Coverage',]

FORCE_SCRIPT_NAME = ''

API_DATETIME_FORMAT = "%Y-%m-%dT%H:%MZ"


CUSTOM_USER_MODEL = "api.Profile"

NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=api,profile',
]

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
            'filename': 'annotation_server.log', #### Path to annotation_server.log file.
            'formatter': 'verbose',
        },
        'django_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'django.log' ##### Path to django.log file.
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

########## Location of PID and socket files.
PID = "/tmp/annotations.pid"
SOCKET = "/tmp/annotations.sock"

try:
    from local_settings import *
except ImportError:
    pass

if 'test' in sys.argv:
    #print "REPLACE DB NAME"
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }

#if 'runserver' in sys.argv:
    #print __file__
    #print DATABASES
