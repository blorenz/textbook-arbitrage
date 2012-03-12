# Django settings for TextbookArb project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#        'NAME': 'ta',                      # Or path to database file if using sqlite3.
#        'USER': 'ta',                      # Not used with sqlite3.
#        'PASSWORD': 'manganello1',                  # Not used with sqlite3.
#        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
#        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
#    },
    'default' : {
      'ENGINE' : 'django_mongodb_engine',
      'NAME' : 'ta_db'
   }
}

#DATABASE_ROUTERS = ['ta.routers.MyAppRouter2',]
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

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

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/virtualenvs/ta/ta/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '___gb4w&68(=8)f!u8koa9wp1k485j*4$p4&rz9ur10kc-%5yo'

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
)

ROOT_URLCONF = 'TextbookArb.urls'

INTERNAL_IPS = ('127.0.0.1',
                '75.22.96.55',
		'63.72.209.229',
                )
TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/virtualenvs/ta/ta/templates'
)

import os
import sys
sys.path.append(os.getcwd())

SITE_ID=u'4f18decf957dae0a7f000000'
#SITE_ID=u'4ec858f7957dae4737000019'
#SITE_ID=u'4ee57c6f957dae447500001d'
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'ta',
    #'south',
    'gunicorn',
    'djangotoolbox',
    'django_mongodb_engine',
)


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


# django-celery
INSTALLED_APPS += ("djcelery", )
INSTALLED_APPS += ("djkombu", )

import djcelery
djcelery.setup_loader()

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "ta"
BROKER_PASSWORD = "colonel1"
BROKER_VHOST = "/ta"

CELERYD_CONCURRENCY = 15 
CELERY_RESULT_BACKEND = "amqp"
CELERY_AMQP_TASK_RESULT_EXPIRES = 30  # 5 hours.
CELERYD_MAX_TASKS_PER_CHILD = 3
CELERYD_TASK_TIME_LIMIT = 900

from datetime import timedelta
from celery.schedules import crontab

#CELERY_QUEUES = {
#    "default": {
#        "exchange": "default",
#        "binding_key": "default"},
#    "quickqueue": {
#        "exchange": "quickq",
#        "exchange_type": "topic",
#        "binding_key": "quickq.quick", 
#    },
#}
#
#CELERY_ROUTES = (
#    {
#        "ta.tasks.updateBCs": {
#            "queue": "quickqueue"
#        },
#    },
#) 

#CELERY_DEFAULT_QUEUE = "default"
#CELERY_DEFAULT_EXCHANGE = "default"
#CELERY_DEFAULT_EXCHANGE_TYPE = "direct"
#CELERY_DEFAULT_ROUTING_KEY = "default"

CELERYBEAT_SCHEDULE = {
#    "runs-every-600-seconds": {
#        "task": "ta.tasks.updateBCs",
#        "schedule": timedelta(seconds=180),
#    },
    # Executes every morning at 4am
#    "every-morning": {
#        "task": "ta.tasks.findNewBooks",
#        "schedule": crontab(hour="*/12"),
#    },
    # Executes every morning at 4am
    "every-evening": {
        "task": "ta.amazon.detailAllBooks",
        "schedule": crontab(hour=19, minute=00,),
    },
    "every-morning3": {
        "task": "ta.amazon.detailAllBooks",
        "schedule": crontab(hour=7, minute=00,),
    },
#    "every-morning2": {
#        "task": "ta.tasks.lookForNewBooks",
#        "schedule": crontab(hour=0, minute=0,),
#    },
}

#end django-celery
