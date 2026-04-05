import os

# Dummy DB values so settings.py's config() calls don't crash during import.
# They are immediately overridden by the SQLite config below.
os.environ.setdefault('DB_NAME', 'unused')
os.environ.setdefault('DB_USER', 'unused')
os.environ.setdefault('DB_PASSWORD', 'unused')

from .settings import *  # noqa: E402, F401, F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

DEBUG = True
ALLOWED_HOSTS = ['*']
