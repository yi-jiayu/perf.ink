"""
Django settings for perf_ink project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path

import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from . import __version__
from .config import config

sentry_sdk.init(
    dsn=config.sentry_dsn,
    integrations=[
        DjangoIntegration(),
    ],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
    release=f"perf-ink@{__version__}"
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.secret_key

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config.debug

ALLOWED_HOSTS = config.allowed_hosts
CSRF_TRUSTED_ORIGINS = config.csrf_trusted_origins
INTERNAL_IPS = [
    "127.0.0.1",
]

# Application definition

INSTALLED_APPS = [
    "app",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "tailwind",
    "theme",
    "debug_toolbar",
    "django_browser_reload",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = "perf_ink.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "perf_ink.context_processors.version",
            ],
        },
    },
]

WSGI_APPLICATION = "perf_ink.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {"default": dj_database_url.parse(config.database_url)}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = ["static"]
STATIC_ROOT = "www/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "app.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = config.account_email_verification

CELERY_BROKER_URL = config.celery_broker_url

TAILWIND_APP_NAME = "theme"

LOGIN_REDIRECT_URL = "/"

EMAIL_HOST = config.email_host
EMAIL_HOST_USER = config.email_host_user
EMAIL_HOST_PASSWORD = config.email_host_password
EMAIL_PORT = 465
EMAIL_USE_SSL = True

if config.default_from_email:
    DEFAULT_FROM_EMAIL = config.default_from_email

if config.server_email:
    SERVER_EMAIL = config.server_email
