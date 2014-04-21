from hashlib import md5
from datetime import timedelta

from django.core import mail
from django.core.urlresolvers import reverse
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


class UserTest(TestCase):

    def test_manager_is_caffeineusermanager(self):
        self.assertIsInstance(User.objects, CaffeineUserManager)

    def test_get_absolute_url(self):
        user = User.objects.create(username='testuser')
        self.assertEqual(user.get_absolute_url(), reverse(
            'public', kwargs={'username': 'testuser'}))

    def test___unicode__(self):
        user = User.objects.create(username='testuser')
        self.assertEqual(unicode(user), '')

        user = User.objects.create(username='testuser2', first_name='Test',
                                   last_name='User', token='foo')
        self.assertEqual(unicode(user), 'Test User')

    def test_export_csv(self):
        user = User.objects.create(username='testuser',
                                   email='testuser@bla.com')
        user.export_csv()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Your caffeine records')
        self.assertEqual(mail.outbox[0].body,
                         'Attached is your caffeine track record.')
        self.assertEqual(mail.outbox[0].recipients()[0], 'testuser@bla.com')
        self.assertEqual(len(mail.outbox[0].attachments), 2)
        self.assertRegexpMatches(mail.outbox[0].attachments[0][0],
                                 r'^coffee-.+\.csv$')
        self.assertRegexpMatches(mail.outbox[0].attachments[1][0],
                                 r'^mate-.+\.csv$')
        self.assertEqual(mail.outbox[0].attachments[0][2], 'text/csv')
        self.assertEqual(mail.outbox[0].attachments[1][2], 'text/csv')
