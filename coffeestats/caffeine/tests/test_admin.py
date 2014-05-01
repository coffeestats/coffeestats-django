from django.test import TestCase
from django.contrib.auth import get_user_model

from caffeine.admin import (
    PASSWORD_MISMATCH_ERROR,
    UserChangeForm,
    UserCreationForm,
)

User = get_user_model()


class UserCreationFormTest(TestCase):

    def test_clean_password2_passwords_match(self):
        form = UserCreationForm(
            data={'username': 'testuser',
                  'email': 'test@bla.com',
                  'password1': 'test1234',
                  'password2': 'test1234'}
        )
        self.assertTrue(form.is_valid(), str(form.errors))
        self.assertEqual(form.cleaned_data['password2'], 'test1234')

    def test_clean_password2_passwords_do_not_match(self):
        form = UserCreationForm(
            data={'username': 'testuser',
                  'email': 'test@bla.com',
                  'password1': 'test1234',
                  'password2': 'test2345'}
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors['password2']), 1)
        self.assertEqual(form.errors['password2'], [PASSWORD_MISMATCH_ERROR])

    def test_save_hash_password(self):
        form = UserCreationForm(
            data={'username': 'testuser',
                  'email': 'test@bla.com',
                  'password1': 'test1234',
                  'password2': 'test1234'}
        )
        user = form.save()
        self.assertTrue(user.check_password('test1234'))


class UserChangeFormTest(TestCase):

    def test_clean_password_returns_hash(self):
        user = User.objects.create_user(
            username='testuser', email='test@example.org', password='test1234')
        form = UserChangeForm(instance=user)
        self.assertEqual(form.clean_password(), user.password)
