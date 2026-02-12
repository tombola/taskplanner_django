"""
Django base settings for taskplanner project.

Shared configuration inherited by all environments.
Environment-specific modules (development.py, production.py, etc.)
import from this file and override as needed.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# Extra .parent since settings is now a package (settings/base.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "django_jsonform",
    "polymorphic",
    "neapolitan",
    # Allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    # Todosync package
    "todosync",
    # Local apps
    "tasks",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "taskplanner.urls"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# URL prefix for reverse proxy deployment
# Set to None for local development, '/tasks' for production
FORCE_SCRIPT_NAME = os.getenv("FORCE_SCRIPT_NAME", None)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "taskplanner.wsgi.application"


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_ROOT = BASE_DIR / "static"

STATICFILES_DIRS = [BASE_DIR / "static_src"]

# Configure static URL with path prefix if behind reverse proxy
if FORCE_SCRIPT_NAME:
    STATIC_URL = f"{FORCE_SCRIPT_NAME}/static/"
else:
    STATIC_URL = "/static/"

# Default primary key field type

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Media files
MEDIA_ROOT = BASE_DIR / "media"
# Configure media URL with path prefix if behind reverse proxy
if FORCE_SCRIPT_NAME:
    MEDIA_URL = f"{FORCE_SCRIPT_NAME}/media/"
else:
    MEDIA_URL = "/media/"

# Logging
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

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
            "filename": str(LOG_DIR / "todosync.log"),
            "maxBytes": 5 * 1024 * 1024,  # 5 MB
            "backupCount": 3,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "todosync": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# Todoist API
TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN", "")
TODOIST_CLIENT_ID = os.getenv("TODOIST_CLIENT_ID", "")
TODOIST_CLIENT_SECRET = os.getenv("TODOIST_CLIENT_SECRET", "")
