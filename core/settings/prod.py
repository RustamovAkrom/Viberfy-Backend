from .base import *
from core.config.cache import * # noqa


DEBUG = False # В продакшене должно быть False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_BOUNCER_HOST"),
        "PORT": os.getenv("POSTGRES_BOUNCER_PORT", 5432),
    }
}
