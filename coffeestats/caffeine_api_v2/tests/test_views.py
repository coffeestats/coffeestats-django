from datetime import datetime

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from caffeine.models import DRINK_TYPES

User = get_user_model()


class CaffeineViewTest(APITestCase):
    def test_create(self):
        """
        Ensure we can create a caffeine entry.
        """
        url = reverse('caffeine-list')
        data = {'ctype': 'coffee', 'date': datetime.now()}
        user = User.objects.create(
            username='test', email='test@example.org', is_staff=True)
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['ctype'], DRINK_TYPES.coffee)
        self.assertTrue(response.data['user'].endswith(
            reverse('user-detail', kwargs={'username': user.username})))
