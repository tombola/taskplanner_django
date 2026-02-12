"""
Django production settings for taskplanner project.

Activate by setting:
    DJANGO_SETTINGS_MODULE=taskplanner.settings.prod
"""

import os
from pathlib import Path

from .base import *  # noqa: F403, F401

SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = False

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "tasks.allotmentplotter.uk").split(",")

CSRF_TRUSTED_ORIGINS = [
    "https://tasks.allotmentplotter.uk",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db" / "db.sqlite3",  # noqa: F405
    }
}

WAGTAILADMIN_BASE_URL = os.getenv("WAGTAILADMIN_BASE_URL", "https://tasks.allotmentplotter.uk")

DRY_RUN_TASK_CREATION = False

# Override log directory to match the mounted volume (/logs in container)
LOG_DIR = Path("/logs")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} {levelname} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "django.log"),
            "maxBytes": 5 * 1024 * 1024,  # 5 MB
            "backupCount": 3,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "tasks": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "todosync": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Django Allauth / Google OAuth
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.getenv("GOOGLE_AUTH_CLIENT_ID", ""),
            "secret": os.getenv("GOOGLE_AUTH_CLIENT_SECRET", ""),
            "key": "",
        },
    },
}
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
