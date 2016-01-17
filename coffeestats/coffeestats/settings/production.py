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

# See: https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = get_env_variable('COFFEESTATS_SITE_ADMINMAIL')
# ######### END EMAIL CONFIGURATION

# ######### CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
# CACHES = {}
# ######### END CACHE CONFIGURATION
