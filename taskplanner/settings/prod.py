"""
Django production settings for taskplanner project.

Activate by setting:
    DJANGO_SETTINGS_MODULE=taskplanner.settings.prod
"""

import os

from .base import *  # noqa: F403, F401

SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'tasks.allotmentplotter.uk').split(',')

CSRF_TRUSTED_ORIGINS = [
    'https://tasks.allotmentplotter.uk',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # noqa: F405
    }
}

WAGTAILADMIN_BASE_URL = os.getenv('WAGTAILADMIN_BASE_URL', 'https://tasks.allotmentplotter.uk')

DEBUG_TASK_CREATION = False
