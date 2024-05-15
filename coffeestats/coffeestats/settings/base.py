# -*- python -*-
# pymode:lint_ignore=E501
"""Common settings and globals."""

import os
from os.path import abspath, basename, dirname, join, normpath
from sys import path

from django.contrib.messages import constants as message_constants
from django.core.exceptions import ImproperlyConfigured


def get_env_variable(var_name, default=None):
    """
    Get a setting from an environment variable.

    :param str var_name: variable name

    """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)


# ######### PATH CONFIGURATION
# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level project folder:
SITE_ROOT = dirname(DJANGO_ROOT)

# Site name:
SITE_NAME = basename(DJANGO_ROOT)

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)
# ######### END PATH CONFIGURATION


# ######### DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False
# ######### END DEBUG CONFIGURATION


# ######### MANAGER CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (("Coffeestats Team", get_env_variable("COFFEESTATS_SITE_ADMINMAIL")),)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = get_env_variable("COFFEESTATS_SITE_ADMINMAIL")

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
# ######### END MANAGER CONFIGURATION


# ######### DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": get_env_variable("COFFEESTATS_PGSQL_DATABASE"),
        "USER": get_env_variable("COFFEESTATS_PGSQL_USER"),
        "PASSWORD": get_env_variable("COFFEESTATS_PGSQL_PASSWORD"),
        "HOST": get_env_variable("COFFEESTATS_PGSQL_HOSTNAME"),
        "PORT": get_env_variable("COFFEESTATS_PGSQL_PORT"),
    }
}
# ######### END DATABASE CONFIGURATION


# ######### GENERAL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
TIME_ZONE = "Europe/Berlin"

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "en-us"

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
SITES_DOMAIN_NAME = get_env_variable("COFFEESTATS_DOMAIN_NAME")
SITES_SITE_NAME = get_env_variable("COFFEESTATS_SITE_NAME")

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = False
# ######### END GENERAL CONFIGURATION


# ######### MEDIA CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = normpath(join(SITE_ROOT, "media"))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"
# ######### END MEDIA CONFIGURATION


# ######### STATIC FILE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = normpath(join(SITE_ROOT, "assets"))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS  # noqa
STATICFILES_DIRS = (normpath(join(SITE_ROOT, "static")),)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders  # noqa
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)
# ######### END STATIC FILE CONFIGURATION


# ######### SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key should only be used for development and testing.
SECRET_KEY = get_env_variable("COFFEESTATS_SITE_SECRET")
# ######### END SECRET CONFIGURATION


# ######### SITE CONFIGURATION
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []
# ######### END SITE CONFIGURATION


# ######### FIXTURE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS  # noqa
FIXTURE_DIRS = (normpath(join(SITE_ROOT, "fixtures")),)
# ######### END FIXTURE CONFIGURATION


# ######### TEMPLATE CONFIGURATION
# See: https://docs.djangoproject.com/en/1.9/ref/settings/#templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": [normpath(join(SITE_ROOT, "templates"))],
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
                "absolute.context_processors.absolute",
                "caffeine.context_processors.mainnav",
            ],
        },
    },
]

# ######### MIDDLEWARE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
MIDDLEWARE = (
    # Default Django middleware.
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # uncomment next line to enable translation to browser locale
    # 'django.middleware.locale.LocaleMiddleware',
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # middleware to redirect user to set timezone
    "caffeine.middleware.EnforceTimezoneMiddleware",
)
# ######### END MIDDLEWARE CONFIGURATION


# ######### URL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "%s.urls" % SITE_NAME
# ######### END URL CONFIGURATION


# ######### APP CONFIGURATION
DJANGO_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.admin",
    "rest_framework",
)

# Apps specific for this project go here.
LOCAL_APPS = (
    "django_registration",
    "caffeine",
    "caffeine_api_v1",
    "caffeine_api_v2",
)

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "caffeine.authbackend.LegacyCoffeestatsAuth",
)

LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "/"
AUTH_USER_MODEL = "caffeine.User"
ACCOUNT_ACTIVATION_DAYS = 2
EMAIL_CHANGE_ACTION_VALIDITY = 2
MINIMUM_DRINK_DISTANCE = 5
CAFFEINE_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

MESSAGE_TAGS = {
    message_constants.DEBUG: "flash-debug",
    message_constants.INFO: "flash-info",
    message_constants.SUCCESS: "flash-success",
    message_constants.WARNING: "flash-warning",
    message_constants.ERROR: "flash-error",
}

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS
# ######### END APP CONFIGURATION


# ######### REST FRAMEWORK CONFIGURATION
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "PAGINATE_BY": 10,
}

# ######### END REST FRAMEWORK CONFIGURATION

API_USAGE_AGREEMENT = "/api/v2/agreement/"

# ######### LOGGING CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(levelname)s %(message)s",
        },
    },
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "caffeine": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
        },
    },
}
# ######### END LOGGING CONFIGURATION


# ######### WSGI CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "%s.wsgi.application" % SITE_NAME
# ######### END WSGI CONFIGURATION

TEST_RUNNER = "django.test.runner.DiscoverRunner"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
