from .production import *  # noqa
from .production import env


# CACHES
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # Mimicing memcache behavior.
            # http://jazzband.github.io/django-redis/latest/#_memcached_exceptions_behavior
            "IGNORE_EXCEPTIONS": True,
        },
    }
}

CACHALOT_ENABLED = True

# STATIC and MEDIA
# ------------------------
INSTALLED_APPS.remove("collectfast")
STATIC_ROOT = ROOT_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MIDDLEWARE.insert(2, "whitenoise.middleware.WhiteNoiseMiddleware")
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"

# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR / "media")
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = env(
    "DJANGO_DEFAULT_FROM_EMAIL",
    default="Donate Anything <noreply@donate-anything.org>",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = env("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = env("DJANGO_EMAIL_SUBJECT_PREFIX", default="[Donate Anything]")

# Anymail + Django SES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
# https://anymail.readthedocs.io/en/stable/installation/#anymail-settings-reference
# https://anymail.readthedocs.io/en/stable/esps/mailgun/
EMAIL_BACKEND = "anymail.backends.amazon_ses.EmailBackend"
ANYMAIL = {"AMAZON_SES_CLIENT_PARAMS": {"region_name": AWS_S3_REGION_NAME}}

# https://github.com/django-ses/django-ses
AWS_SES_CONFIGURATION_SET = "donate-anything"
AWS_SES_VERIFY_BOUNCE_SIGNATURES = True

# django-compressor
# ------------------------------------------------------------------------------
# https://django-compressor.readthedocs.io/en/latest/settings/#django.conf.settings.COMPRESS_ENABLED
COMPRESS_ENABLED = env.bool("COMPRESS_ENABLED", default=True)
# https://django-compressor.readthedocs.io/en/latest/settings/#django.conf.settings.COMPRESS_OFFLINE
COMPRESS_OFFLINE = True
# https://django-compressor.readthedocs.io/en/latest/settings/#django.conf.settings.COMPRESS_STORAGE
# https://django-compressor.readthedocs.io/en/latest/remote-storages/#using-staticfiles
COMPRESS_STORAGE = "compressor.storage.GzipCompressorFileStorage"
COMPRESS_ROOT = STATIC_ROOT
# https://django-compressor.readthedocs.io/en/latest/settings/#django.conf.settings.COMPRESS_URL
COMPRESS_URL = STATIC_URL

# Your stuff...
# ------------------------------------------------------------------------------
AXES_META_PRECEDENCE_ORDER = [
    "HTTP_X_FORWARDED_FOR",
    "REMOTE_ADDR",
]
