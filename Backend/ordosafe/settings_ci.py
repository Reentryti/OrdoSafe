import os
from cryptography.fernet import Fernet

# Set dummy env vars BEFORE importing settings, so config() calls don't fail.
# These values are never used — they get overridden below or are only needed
# by services (Twilio) that CI never calls.
os.environ.setdefault('SECRET_KEY', 'ci-test-secret-key')
os.environ.setdefault('DB_NAME', 'unused')
os.environ.setdefault('DB_USER', 'unused')
os.environ.setdefault('DB_PASSWORD', 'unused')
os.environ.setdefault('FERNET_KEY', Fernet.generate_key().decode())
os.environ.setdefault('TWILIO_ACCOUNT_SID', 'fake')
os.environ.setdefault('TWILIO_AUTH_TOKEN', 'fake')
os.environ.setdefault('TWILIO_PHONE_NUMBER', '+10000000000')

from .settings import *  # noqa: E402, F401, F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

DEBUG = True
ALLOWED_HOSTS = ['*']
