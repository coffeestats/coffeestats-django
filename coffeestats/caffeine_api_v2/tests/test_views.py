from __future__ import unicode_literals, print_function

from datetime import datetime

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


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
