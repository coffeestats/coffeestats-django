from __future__ import unicode_literals

from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from unittest.mock import MagicMock
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from caffeine.models import Caffeine, DRINK_TYPES
from caffeine_api_v2.serializers import (
    CaffeineSerializer,
    UserSerializer,
    CaffeineField, UserCaffeineSerializer)

User = get_user_model()


class CaffeineFieldTest(TestCase):
    def setUp(self):
        super(CaffeineFieldTest, self).setUp()
        self.subject = CaffeineField()

    def test_to_representation_valid_key(self):
        for key, attr, _ in DRINK_TYPES._triples:
            self.assertEqual(self.subject.to_representation(key), attr)

    def test_to_representation_invalid_key(self):
        with self.assertRaisesMessage(
                RuntimeError,
                "Could not map database internal id invalid to value"):
            self.subject.to_representation('invalid')

    def test_to_internal_value(self):
        for drink_type in ['coffee', 'mate']:
            self.assertEqual(
                self.subject.to_internal_value(drink_type),
                getattr(DRINK_TYPES, drink_type))


class CaffeineSerializerTest(TestCase):
    def setUp(self):
        super(CaffeineSerializerTest, self).setUp()
        user = User.objects.create_user('test', 'test@example.org')
        now = datetime.now()
        coffee = Caffeine.objects.create(
            ctype=DRINK_TYPES.coffee, user=user, date=now)
        self.subject = CaffeineSerializer(coffee)

    def test_is_expected_serializer(self):
        self.assertIsInstance(self.subject, CaffeineSerializer)

    def test_validate(self):
        user = User.objects.create_user(
            username='testuser', email='test@example.org', password='s3cr3t',
            timezone='Europe/Berlin'
        )
        first_caff = Caffeine.objects.create(
            ctype=DRINK_TYPES.coffee, date=timezone.now(), user=user)
        first_caff.save()
        data = {
            'user': user,
            'date': timezone.now(),
            'timezone': user.timezone,
            'ctype': 'coffee',
        }
        with self.assertRaises(ValidationError):
            self.subject.run_validation(data)


class UserCaffeineSerializerTest(TestCase):
    def setUp(self):
        super(UserCaffeineSerializerTest, self).setUp()
        self.user = User.objects.create_user(
            'test', 'test@example.org',
            timezone='Europe/Berlin')
        self.mockview = MagicMock(view_owner=self.user)

    def test_save_no_timezone(self):
        subject = UserCaffeineSerializer(
            data={'date': datetime.now(), 'ctype': 'coffee'},
            context={'view': self.mockview})
        self.assertTrue(subject.is_valid(True))
        saved = subject.save()
        self.assertIsInstance(saved, Caffeine)
        self.assertEqual(saved.timezone, self.user.timezone)

    def test_save_with_timezone(self):
        subject = UserCaffeineSerializer(
            data={'date': datetime.now(), 'ctype': 'coffee',
                  'timezone': 'Arctic/Longyearbyen'},
            context={'view': self.mockview})
        self.assertTrue(subject.is_valid(True))
        saved = subject.save()
        self.assertIsInstance(saved, Caffeine)
        self.assertEqual(saved.timezone, 'Arctic/Longyearbyen')

    def test_validate(self):
        subject = UserCaffeineSerializer(
            data={'date': datetime.now(), 'ctype': 'coffee'},
            context={'view': self.mockview})
        first_caff = Caffeine.objects.create(
            ctype=DRINK_TYPES.coffee, date=timezone.now(), user=self.user)
        first_caff.save()
        data = {
            'date': timezone.now(),
            'ctype': 'coffee',
        }
        with self.assertRaises(ValidationError):
            subject.run_validation(data)


class UserSerializerTest(TestCase):
    def setUp(self):
        super(UserSerializerTest, self).setUp()
        self.user = User.objects.create_user(
            'test', 'test@example.org', first_name='Test', last_name='User',
            is_active=True)
        self.request = APIRequestFactory().get(
            reverse('user-detail', kwargs={'username': self.user.username}))
        self.subject = UserSerializer(
            self.user, context={'request': self.request})

    def test_is_expected_serializer(self):
        self.assertIsInstance(self.subject, UserSerializer)

    def test_name(self):
        self.assertEqual(self.subject.data['name'], self.user.get_full_name())

    def test_get_profile_url(self):
        self.assertEqual(
            self.subject.data['profile'],
            reverse(
                'public', kwargs={'username': self.user.username},
                request=self.request)
        )

    def test_caffeines_url(self):
        self.assertEqual(
            self.subject.data['caffeines'],
            reverse(
                'user-caffeine-list', kwargs={
                    'caffeine_username': self.user.username
                }, request=self.request)
        )
