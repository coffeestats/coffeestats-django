from django.test import TestCase

from django.contrib.auth.hashers import check_password

from passlib.hash import bcrypt

from .models import User
from .authbackend import LegacyCoffeestatsAuth


class LegacyCoffeestatsAuthTest(TestCase):
    def setUp(self):
        user, created = User.objects.get_or_create(
            username='testuser')
        user.cryptsum = bcrypt.encrypt('test', ident='2y')
        user.password = ''
        user.save()

    def test_authenticate(self):
        legacyauth = LegacyCoffeestatsAuth()
        assert legacyauth.authenticate('nouser', 'doesntmatter') is None

        assert legacyauth.authenticate('testuser', 'wrong') is None

        loggedin = legacyauth.authenticate('testuser', 'test')
        assert loggedin is not None
        assert loggedin.cryptsum == ''
        assert check_password('test', loggedin.password)

        assert legacyauth.get_user(loggedin.id) == loggedin
        assert legacyauth.get_user(-10) is None
