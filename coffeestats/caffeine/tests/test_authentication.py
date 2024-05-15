from django.test import TestCase

from django.contrib.auth.hashers import check_password

from passlib.hash import bcrypt

from caffeine.models import User
from caffeine.authbackend import LegacyCoffeestatsAuth


class LegacyCoffeestatsAuthTest(TestCase):
    def setUp(self):
        self.user, created = User.objects.get_or_create(username="testuser")
        self.user.cryptsum = bcrypt.hash("test", ident="2y")
        self.user.password = ""
        self.user.save()

        self.legacyauth = LegacyCoffeestatsAuth()

    def test_authenticate_nonexistant_user(self):
        self.assertIsNone(self.legacyauth.authenticate("nouser", "doesntmatter"))

    def test_authenticate_user_with_wrong_password(self):
        self.assertIsNone(self.legacyauth.authenticate("testuser", "wrong"))

    def test_authenticate_valid_user(self):
        loggedin = self.legacyauth.authenticate("testuser", "test")

        self.assertIsNotNone(loggedin)
        self.assertEqual(loggedin.cryptsum, "")
        self.assertTrue(check_password("test", loggedin.password))

        self.assertEqual(self.legacyauth.get_user(loggedin.id), loggedin)

    def test_authenticate_only_works_once(self):
        """
        Check that subsequent authentication fails, because user has been
        migrated.
        """
        self.assertIsNotNone(self.legacyauth.authenticate("testuser", "test"))
        self.assertIsNone(self.legacyauth.authenticate("testuser", "test"))

    def test_get_nonexistent_user(self):
        self.assertIsNone(self.legacyauth.get_user(-10))

    def test_get_existant_user(self):
        self.assertEqual(self.legacyauth.get_user(self.user.id), self.user)
