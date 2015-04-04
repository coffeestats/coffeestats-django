from datetime import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from caffeine.models import Caffeine, DRINK_TYPES

from caffeine_api_v2.serializers import (
    CaffeineSerializer,
    UserSerializer,
)

User = get_user_model()


class CaffeineSerializerTest(TestCase):
    def setUp(self):
        super(CaffeineSerializerTest, self).setUp()
        user = User.objects.create(username='test', email='test@example.org')
        now = datetime.now()
        coffee = Caffeine.objects.create(
            ctype=DRINK_TYPES.coffee, user=user, date=now)
        self.subject = CaffeineSerializer(coffee)

    def test_is_expected_serializer(self):
        self.assertIsInstance(self.subject, CaffeineSerializer)


class UserSerializerTest(TestCase):
    def setUp(self):
        super(UserSerializerTest, self).setUp()
        self.user = User.objects.create(
            username='test', first_name='Test', last_name='User',
            email='test@example.org')
        self.request = APIRequestFactory().get(
            reverse('user-detail', kwargs={'username': self.user.username}))
        self.subject = UserSerializer(
            self.user, context={'request': self.request})

    def test_is_expected_serializer(self):
        self.assertIsInstance(self.subject, UserSerializer)

    def test_name(self):
        self.assertEqual(self.subject.data['name'], self.user.get_full_name())

    def test_get_profile(self):
        self.assertEqual(
            self.subject.data['profile'],
            reverse(
                'public', kwargs={'username': self.user.username},
                request=self.request)
        )

    def test_coffees(self):
        self.assertEqual(self.subject.data['coffees'], 0)

    def test_mate(self):
        self.assertEquals(self.subject.data['mate'], 0)
