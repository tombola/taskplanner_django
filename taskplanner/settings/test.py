"""
Django test settings for taskplanner project.

Activate by setting:
    DJANGO_SETTINGS_MODULE=taskplanner.settings.test
"""

from .base import *  # noqa: F403, F401

SECRET_KEY = 'django-insecure-test-key-not-for-production'

DEBUG = False

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Faster password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

WAGTAILADMIN_BASE_URL = 'http://localhost:8000'

DEBUG_TASK_CREATION = True
