import os
from fnmatch import fnmatch
from django.conf import global_settings
from varlet import variable

PROJECT_DIR = os.path.dirname(__file__)
HOME_DIR = os.path.normpath(os.path.join(PROJECT_DIR, '../'))

DEBUG = variable("DEBUG", False)
TEMPLATE_DEBUG = DEBUG

# [('Your Name', 'your_email@example.com')]
ADMINS = variable("ADMINS", [])

MANAGERS = ADMINS

SERVER_EMAIL = 'django@pdx.edu'

CAS_SERVER_URL = 'https://sso.pdx.edu/cas/login'

AUTH_USER_MODEL = 'models.AdminUser'

# allow the use of wildcards in the INTERAL_IPS setting
class IPList(list):
    # do a unix-like glob match
    # E.g. '192.168.1.100' would match '192.*'
    def __contains__(self, ip):
        for ip_pattern in self:
            if fnmatch(ip, ip_pattern):
                return True
        return False

INTERNAL_IPS = IPList(['10.*', '192.168.*'])

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['.pdx.edu']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'US/Pacific'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(HOME_DIR, "static")

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = "/static/"

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR, "static"),
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'djangocas.backends.CASBackend',
)

ROOT_URLCONF = 'mussels.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'mussels.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR, "templates"),
)

INSTALLED_APPS = (
    #'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'mussels.models',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

# supress a warning
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        # the Atlas of Oregon Lakes (AOL), and this mussels project share a
        # database (AOL uses the public schema, mussels uses the mussels
        # schema), but during development, you can use an isolated DB
        'NAME': variable("DB_NAME", 'mussels'),
        'USER': variable("DB_USER", 'root'),
        'PASSWORD': variable("DB_PASSWORD", ''),
        'HOST': variable("DB_HOST", ''),
        'PORT': '',
        'OPTIONS': {
            # add the mussels schema to the search path, which is useful in production
            'options': '-c search_path=mussels,public',
        }
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = variable("SECRET_KEY", os.urandom(64).decode("latin1"))
