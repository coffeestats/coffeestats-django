from unittest import TestCase


class WSGITest(TestCase):

    def test_wsgi_application(self):
        from coffeestats import wsgi
        self.assertIsNotNone(wsgi.application)
