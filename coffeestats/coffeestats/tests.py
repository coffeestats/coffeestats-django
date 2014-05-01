import os
from unittest import TestCase

from django.core.exceptions import ImproperlyConfigured

from coffeestats.settings.base import get_env_variable


class GetEnvVariableTest(TestCase):

    def test_get_existing_env_variable(self):
        os.environ['testvariable'] = 'myvalue'
        self.assertEqual(get_env_variable('testvariable'), 'myvalue')

    def test_get_missing_env_variable(self):
        if 'missingvariable' in os.environ:
            del os.environ['missingvariable']
        try:
            get_env_variable('missingvariable')
            self.fail('should have raised ImproperlyConfigured')
        except Exception as e:
            self.assertIsInstance(e, ImproperlyConfigured)
            self.assertEqual(
                str(e), 'Set the missingvariable environment variable')


class WSGITest(TestCase):

    def test_wsgi_application(self):
        from coffeestats import wsgi
        self.assertIsNotNone(wsgi.application)
