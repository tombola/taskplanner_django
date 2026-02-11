"""
Django development settings for taskplanner project.

Used for local development. This is the default when no
DJANGO_SETTINGS_MODULE is explicitly set.
"""

from .base import *  # noqa: F403, F401

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-(llgrb%l(e1#2^i3ol0=&-seca+($xbm=(gq9@1s&c@w_r%%&b"

DEBUG = True

ALLOWED_HOSTS = [
    "taskplanner.local",
    "tasks.localhost",
    "localhost",
    "127.0.0.1",
    "vestigially-plagal-emiko.ngrok-free.dev",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

INSTALLED_APPS += ["django_browser_reload", "django_extensions"]  # noqa: F405

MIDDLEWARE += ["django_browser_reload.middleware.BrowserReloadMiddleware"]  # noqa: F405

# Task creation dry run mode
# When True, task creation will log planned actions instead of posting to Todoist API
DRY_RUN_TASK_CREATION = os.getenv("DRY_RUN_TASK_CREATION", "False").lower() in ("true", "1", "yes")  # noqa: F405
