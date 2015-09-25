# Django settings for Econsensus project.

import os
import sys
import private_settings  # @UnresolvedImport

DJANGO_HOME = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Econsensus Project', 'carers-econsensus@aptivate.org'),
)

ALLOWED_HOSTS = [
    '.econsensus.org',
    'www.econsensus.org',
    'econsensus.stage.aptivate.org',
    'fen-vz-econsensus.fen.aptivate.org',
]

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',  # Or path to database file if using sqlite3.
        'USER': '',  # Not used with sqlite3.
        'PASSWORD': '',  # Not used with sqlite3.
        'HOST': '',  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',  # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-GB'

# Need to figure out what this means...
SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(DJANGO_HOME, 'media')

MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(DJANGO_HOME, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

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
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = private_settings.SECRET_KEY

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'waffle.middleware.WaffleMiddleware',
)

ROOT_URLCONF = 'econsensus.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(DJANGO_HOME, "templates"),
    os.path.join(DJANGO_HOME, "publicweb/templates"),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "publicweb.context_processors.current_site.current_site",
    "publicweb.context_processors.version.version",
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)

INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.comments',
    'django.contrib.flatpages',
    'django.contrib.markup',
    'south',
    'registration',
    'waffle',
    'notification',
    'custom_comments',
    'keyedcache',
    'livesettings',
    'organizations',
    'custom_organizations',
    'guardian',
    'publicweb',
    'signals',
    'tinymce',
    'tagging',
    'remember_me',
    'actionitems',
    'custom_flatpages',
    'haystack',
    'custom_haystack'
)

ACTIONITEMS_ORIGIN_MODEL = 'publicweb.Decision'

# Search disabled by default.
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'custom_haystack.backends.disabled_backend.DisabledEngine',
    },
}

# When search is enabled, updates to search index happens
# in real time.
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend'
)

ANONYMOUS_USER_ID = -1

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

LOG_DIR = os.path.join(DJANGO_HOME, 'log')
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)
LOG_FILE = os.path.join(LOG_DIR, 'econsensus.log')
if not os.path.exists(LOG_FILE):
    open(LOG_FILE, 'w').close()


# Stop SuspiciousOperation errors being sent through - a workaround until
# we upgrade to Django 1.6 (which has a proper fix). References:
# - http://www.tiwoc.de/blog/2013/03/django-prevent-email-notification-on-suspiciousoperation/
# - https://code.djangoproject.com/ticket/19866
# - http://stackoverflow.com/questions/15238506/djangos-suspiciousoperation-invalid-http-host-header
from django.core.exceptions import SuspiciousOperation


def skip_suspicious_operations(record):
    if record.exc_info:
        exc_value = record.exc_info[1]
        if isinstance(exc_value, SuspiciousOperation):
            return False
    return True


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s: %(asctime)s [%(module)s] %(message)s',
        },
        'simple': {
            'format': '%(levelname)s: %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'utils.log.RequireDebugFalse',
        },
        'skip_suspicious_operations': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_suspicious_operations,
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false', 'skip_suspicious_operations'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'file': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': LOG_FILE
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'econsensus': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        }
    }
}

# Set this to true to log emails marked as auto-replies. Default is False
LOG_AUTO_REPLIES = True

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'

TINYMCE_DEFAULT_CONFIG = {
    "theme": "advanced",
    "theme_advanced_buttons1": "bold,italic,underline,link,unlink,"
                               "bullist,blockquote,undo",
    "theme_advanced_buttons2": "",
    "theme_advanced_buttons3": ""
}


# Emails from organizations will be built around this address
DEFAULT_FROM_EMAIL = 'econsensus@econsensus.org'

# Required for djangoregistration:
ACCOUNT_ACTIVATION_DAYS = 7

# using custom comments app
COMMENTS_APP = 'custom_comments'

# Requirements for django-keyedcache, which is a requirement of django-livesettings.
CACHE_PREFIX = str(SITE_ID)
CACHE_TIMEOUT = 0
import logging
logging.getLogger('keyedcache').setLevel(logging.INFO)

TEST_RUNNER = 'test_runner.DiscoveryRunner'

# tests will go quite a bit faster, particularly when users are created
# in almost every test
if 'test' in sys.argv:
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
        'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
    )

# Override invitation email templates
INVITATION_BACKEND = "custom_organizations.invitation_backend.CustomInvitationBackend"

#--------------------------------
# local settings import
# from http://djangosnippets.org/snippets/1873/
#--------------------------------
try:
    import local_settings
except ImportError:
    print """
    -------------------------------------------------------------------------
    You need to create a local_settings.py file.
    -------------------------------------------------------------------------
    """
    import sys
    sys.exit(1)
else:
    # Import any symbols that begin with A-Z. Append to lists any symbols that
    # begin with "EXTRA_".
    import re
    for attr in dir(local_settings):
        match = re.search('^EXTRA_(\w+)', attr)
        if match:
            name = match.group(1)
            value = getattr(local_settings, attr)
            try:
                globals()[name] += value
            except KeyError:
                globals()[name] = value
        elif re.search('^[A-Z]', attr):
            globals()[attr] = getattr(local_settings, attr)

        if attr == 'LOG_FILE':
            LOGGING['handlers']['file']['filename'] = LOG_FILE
            if not os.path.exists(LOG_FILE):
                open(LOG_FILE, 'w').close()
