from __future__ import unicode_literals

from django.test import TestCase

from caffeine_oauth2.models import CoffeestatsApplication


class CoffeestatsApplicationTest(TestCase):
    def test___str__(self):
        application = CoffeestatsApplication(name='test', client_id='client')
        self.assertEquals(str(application), 'test client')
