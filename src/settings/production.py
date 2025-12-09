"""generated with djinit"""

from .base import *  # noqa: F403, F405

DEBUG = False
SECRET_KEY = env("SECRET_KEY")  # noqa: F405
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])  # noqa: F405

# Database
# Using dj_database_url (recommended for production)
DATABASES = {"default": env.db("DATABASE_URL")}  # noqa: F405

# CORS settings for production
# Filter out empty strings from FRONTEND_URL

# Additional CORS security for production
CORS_ALLOW_PRIVATE_NETWORK = False

# Email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST")  # noqa: F405
EMAIL_PORT = env.int("EMAIL_PORT", default=587)  # noqa: F405
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)  # noqa: F405
EMAIL_HOST_USER = env("EMAIL_HOST_USER")  # noqa: F405
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")  # noqa: F405
DEFAULT_FROM_EMAIL = env("EMAIL_HOST_USER")  # noqa: F405
SERVER_EMAIL = env("EMAIL_HOST_USER")  # noqa: F405

# Security settings for production
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Session settings
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Static files
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
