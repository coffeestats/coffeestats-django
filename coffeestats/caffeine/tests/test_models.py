from hashlib import md5
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone


from caffeine.models import CaffeineUserManager, User


class CaffeineUserManagerTest(TestCase):

    def _populate_some_testusers(self):
        for num in range(10):
            User.objects.create(
                username='test{}'.format(num + 1),
                token='testtoken{}'.format(num + 1),
                date_joined=timezone.now() - timedelta(days=num))

    def test_create_user_empty_username(self):
        with self.assertRaisesRegexp(
                ValueError, 'User must have a username.'):
            User.objects.create_user('', '')

    def test_create_user_empty_email(self):
        with self.assertRaisesRegexp(
                ValueError, 'User must have an email address.'):
            User.objects.create_user('testuser', '')

    def test_create_user_with_no_password(self):
        user = User.objects.create_user('testuser', 'test@bla.com')
        self.assertEqual(user.token, '')

    def test_create_user_with_password(self):
        user = User.objects.create_user('testuser', 'test@bla.com', 'password')
        self.assertEqual(user.token, md5('testuserpassword').hexdigest())
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.public)

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            'testadmin', 'admin@bla.com', 's3cr3t')
        self.assertEqual(user.token, md5('testadmins3cr3t').hexdigest())
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.public)

    def test_random_users_no_users(self):
        random = [u for u in User.objects.random_users()]
        self.assertEqual(len(random), 0)

    def test_random_users_existing_users(self):
        self._populate_some_testusers()
        random = [u for u in User.objects.random_users()]
        self.assertEqual(len(random), 4)

    def test_recently_joined(self):
        self._populate_some_testusers()
        users = [u.username for u in User.objects.recently_joined()]
        self.assertEqual(len(users), 5)
        self.assertEqual(users, ['test1', 'test2', 'test3', 'test4', 'test5'])

    def test_longest_joined(self):
        self._populate_some_testusers()
        users = [u.username for u in User.objects.longest_joined()]
        self.assertEqual(len(users), 5)
        self.assertEqual(users, ['test10', 'test9', 'test8', 'test7', 'test6'])
