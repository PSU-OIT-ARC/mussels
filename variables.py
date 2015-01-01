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
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

DEBUG = True

DB_ENGINE = 'django.contrib.gis.db.backends.postgis'

# Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
DB_NAME = 'mussels'

# Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
# Or path to database file if using sqlite3.
# The following settings are not used with sqlite3:
DB_USER = ''

DB_PASSWORD = ''

DB_HOST = ''

# Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
DB_PORT = ''

DB_OPTIONS = '-c search_path=mussels,public'

# Make this unique, and don't share it with anybody.
SECRET_KEY = "t\\'Óü[,\x9d¦L¶\x18øÑm\x9b1´\x8aéá\x17ë\x0eÜåF\x8dpSí\t©\x84\x97\x85\x17¬\x9f\x8cjÜ\x18Z\x9b\x82vô\x17\x07*}ÌüÁ\x11¢\x91ãÚ\x1eÃÖæ"
