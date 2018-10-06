from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from caffeine_oauth2.models import CoffeestatsApplication

User = get_user_model()


class CoffeestatsApplicationTest(TestCase):
    def test___str__(self):
        application = CoffeestatsApplication(name='test', client_id='client')
        self.assertEquals(str(application), 'test client')

    def test_get_absolute_url_unapproved(self):
        application = CoffeestatsApplication(name='test', client_id='client',
                                             pk=1)
        self.assertEqual(
            application.get_absolute_url(),
            reverse('oauth2_provider:detail', kwargs={'pk': 1}))

    def test_get_absolute_url_approved(self):
        application = CoffeestatsApplication(name='test', client_id='client',
                                             pk=1, approved=True)
        self.assertEqual(
            application.get_absolute_url(),
            reverse('oauth2_provider:detail', kwargs={'pk': 1}))

    def test_approve(self):
        application = CoffeestatsApplication(name='test', client_id='client')
        self.assertFalse(application.approved)
        self.assertIsNone(application.approved_by_id)
        self.assertIsNone(application.approved_on)
        user = User(username='tester')
        application.approve(user)
        self.assertTrue(application.approved)
        self.assertEqual(application.approved_by, user)
        self.assertIsNotNone(application.approved_on)

    def test_reject(self):
        user = User.objects.create_user('tester', 'test@example.org')
        application = CoffeestatsApplication.objects.create(
            name='test', agree=False, user=user)
        client_id = application.client_id
        self.assertIsNotNone(client_id)
        found = CoffeestatsApplication.objects.get(client_id=client_id)
        self.assertEqual(found, application)
        found.reject()
        with self.assertRaises(CoffeestatsApplication.DoesNotExist):
            CoffeestatsApplication.objects.get(client_id=client_id)
