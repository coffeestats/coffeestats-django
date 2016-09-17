from __future__ import unicode_literals, print_function

from datetime import datetime

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from caffeine.models import Caffeine, DRINK_TYPES

User = get_user_model()


class CaffeineViewTest(APITestCase):
    def test_create(self):
        """
        Ensure we can create a caffeine entry.
        """
        user = User.objects.create_user(
            username='test', email='test@example.org')
        url = reverse(
            'user-caffeine-list',
            kwargs={'caffeine_username': 'test'})
        data = {'ctype': 'coffee', 'date': datetime.now()}
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['ctype'], 'coffee')
        self.assertTrue(response.data['user'].is_hyperlink)
        self.assertTrue(
            response.data['user'].endswith(reverse(
                'user-detail', kwargs={'username': user.username})))
        self.assertTrue(response.data['url'].is_hyperlink)
        self.assertIn('entrytime', response.data)
        self.assertIn('timezone', response.data)


class UserCaffeineViewSetTest(APITestCase):
    def test_get_queryset(self):
        user = User.objects.create_user(
            username='test', email='test@example.org')
        url = reverse(
            'user-caffeine-list',
            kwargs={'caffeine_username': user.username})
        self.client.force_authenticate(user=user)
        response = self.client.get(url)
        self.assertIsNotNone(response)
        self.assertEqual(len(response.data), 0)

    def test_has_user_caffeine(self):
        user = User.objects.create_user(
            username='test', email='test@example.org')
        now = timezone.now()
        Caffeine.objects.create(user=user, ctype=DRINK_TYPES.coffee, date=now)
        Caffeine.objects.create(user=user, ctype=DRINK_TYPES.mate, date=now)

        url = reverse(
            'user-caffeine-list',
            kwargs={'caffeine_username': user.username})
        self.client.force_authenticate(user=user)
        response = self.client.get(url)
        self.assertIsNotNone(response)
        data = response.data
        self.assertEqual(len(data), 2)
        self.assertTrue(data[0]['url'].is_hyperlink)
        self.assertTrue(data[1]['url'].is_hyperlink)
        self.assertTrue(
            data[0]['user'].endswith(reverse(
                'user-detail', kwargs={'username': user.username})))
        self.assertTrue(
            data[1]['user'].endswith(reverse(
                'user-detail', kwargs={'username': user.username})))