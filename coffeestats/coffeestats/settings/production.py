# -*- python -*-
# pymode:lint_ignore=W0401,E501
"""Production settings and globals."""

from __future__ import absolute_import

from .base import *  # noqa  intended behaviour

# ######### HOST CONFIGURATION
# See: https://docs.djangoproject.com/en/1.5/releases/1.5/#allowed-hosts-required-in-production  # noqa
ALLOWED_HOSTS = [SITES_DOMAIN_NAME]
# ######### END HOST CONFIGURATION

# ######### EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME

EMAIL_HOST = env('COFFEESTATS_EMAIL_HOST')
EMAIL_PORT = env.int('COFFEESTATS_EMAIL_PORT')
EMAIL_USE_TLS = env.bool('COFFEESTATS_EMAIL_USE_TLS', default=False)
EMAIL_USE_SSL = env.bool('COFFEESTATS_EMAIL_USE_SSL', default=False)
EMAIL_HOST_USER = env('COFFEESTATS_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('COFFEESTATS_EMAIL_HOST_PASSWORD')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = env('COFFEESTATS_SITE_ADMINMAIL')
# ######### END EMAIL CONFIGURATION

# ######### CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
# CACHES = {}
# ######### END CACHE CONFIGURATION
