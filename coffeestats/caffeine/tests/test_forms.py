from datetime import timedelta

from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from caffeine.forms import (
    CoffeestatsRegistrationForm,
    DUPLICATE_EMAIL_ERROR,
    DUPLICATE_USER_ERROR,
    EMPTY_TIMEZONE_ERROR,
    INVALID_TIMEZONE_ERROR,
    PASSWORD_MISMATCH_ERROR,
    SelectTimeZoneForm,
    SettingsForm,
    SubmitCaffeineForm,
)
from caffeine.models import (
    Action,
    ACTION_TYPES,
    Caffeine,
    DRINK_TYPES,
)


User = get_user_model()


class CoffeestatsRegistrationFormTest(TestCase):

    def test_clean_username_new_user(self):
        form = CoffeestatsRegistrationForm(
            data={'username': 'testuser',
                  'email': 'test@bla.com',
                  'password1': 'test1234',
                  'password2': 'test1234'}
        )
        self.assertTrue(form.is_valid(), str(form.errors))
        self.assertEqual(form.clean_username(), 'testuser')

    def test_clean_username_existing_user(self):
        User.objects.create_user('testuser', 'test@bla.com')
        form = CoffeestatsRegistrationForm(
            data={'username': 'testuser',
                  'email': 'test@example.org',
                  'password1': 'test1234',
                  'password2': 'test1234'}
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], [DUPLICATE_USER_ERROR])

    def test_clean_email_new_user(self):
        form = CoffeestatsRegistrationForm(
            data={'username': 'testuser',
                  'email': 'test@bla.com',
                  'password1': 'test1234',
                  'password2': 'test1234'}
        )
        self.assertTrue(form.is_valid(), str(form.errors))
        self.assertEqual(form.clean_email(), 'test@bla.com')

    def test_clean_email_existing_email(self):
        User.objects.create_user('testuser', 'test@bla.com')
        form = CoffeestatsRegistrationForm(
            data={'username': 'testuser2',
                  'email': 'test@bla.com',
                  'password1': 'test1234',
                  'password2': 'test1234'}
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], [DUPLICATE_EMAIL_ERROR])


class SettingsFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@bla.com',
            password='test1234')

    def test_clean_password2_empty(self):
        form = SettingsForm(data={}, instance=self.user)
        self.assertTrue(form.is_valid())
        self.assertTrue(self.user.check_password('test1234'))

    def test_clean_password2_valid(self):
        self.assertTrue(self.user.check_password('test1234'))
        form = SettingsForm(data={
            'password1': 'test2345',
            'password2': 'test2345'
        }, instance=self.user)
        self.assertTrue(form.is_valid())
        self.assertTrue(self.user.check_password('test2345'))

    def test_clean_password2_invalid(self):
        self.assertTrue(self.user.check_password('test1234'))
        form = SettingsForm(data={
            'password1': 'test2345',
            'password2': 'wrongone'
        }, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password2'],
                         [PASSWORD_MISMATCH_ERROR])
        self.assertTrue(self.user.check_password('test1234'))

    def test_clean_password2_one_empty(self):
        form = SettingsForm(data={
            'password1': 'test2345',
            'password2': ''
        }, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password2'],
                         [PASSWORD_MISMATCH_ERROR])
        self.assertTrue(self.user.check_password('test1234'))

    def test_clean_email_no_change(self):
        form = SettingsForm(data={
            'email': 'test@bla.com'}, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_clean_email_change_user(self):
        form = SettingsForm(data={
            'email': 'test@blub.com'}, instance=self.user)
        self.assertTrue(form.is_valid())
        self.assertEqual(len(Action.objects.all()), 1)
        self.assertEqual(Action.objects.all()[0].data, 'test@blub.com')
        self.assertEqual(Action.objects.all()[0].user, self.user)
        self.assertEqual(Action.objects.all()[0].atype,
                         ACTION_TYPES.change_email)

    def test_clean_email_duplicate_address(self):
        User.objects.create_user(username='testuser2', email='test@blub.com')
        form = SettingsForm(data={
            'email': 'test@blub.com'}, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], [DUPLICATE_EMAIL_ERROR])


class SelectTimeZoneFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@bla.com',
            password='test1234')

    def test_clean_timezone_empty(self):
        form = SelectTimeZoneForm(data={}, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['timezone'], [EMPTY_TIMEZONE_ERROR])

    def test_clean_timezone_invalid(self):
        form = SelectTimeZoneForm(
            data={'timezone': 'INVALIDBYINTENT'}, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['timezone'], [INVALID_TIMEZONE_ERROR])

    def test_clean_timezone_valid(self):
        form = SelectTimeZoneForm(
            data={'timezone': 'Europe/Berlin'}, instance=self.user)
        self.assertTrue(form.is_valid())


class SubmitCaffeineFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@bla.com',
            password='test1234')
        self.user.timezone = 'Europe/Berlin'

    def test_clean_no_previous(self):
        now = timezone.now()
        form = SubmitCaffeineForm(
            self.user, DRINK_TYPES.coffee,
            data={'date': now.date(), 'time': now.time()})
        self.assertTrue(form.is_valid(), str(form.errors))

    def test_save_with_passed_data(self):
        now = timezone.now()
        caffeine = SubmitCaffeineForm(
            self.user, DRINK_TYPES.coffee,
            data={'date': now.date(), 'time': now.time()}
        ).save()
        self.assertLessEqual(caffeine.date, timezone.now())
        self.assertEqual(caffeine.ctype, DRINK_TYPES.coffee)
        self.assertEqual(caffeine.user, self.user)
        self.assertEqual(caffeine.timezone, 'Europe/Berlin')

    def test_clean_old_previous(self):
        Caffeine.objects.create(
            user=self.user, ctype=DRINK_TYPES.coffee,
            date=timezone.now() - timedelta(minutes=10))
        now = timezone.now()
        form = SubmitCaffeineForm(
            self.user, DRINK_TYPES.coffee,
            data={'date': now.date(), 'time': now.time()})
        self.assertTrue(form.is_valid(), str(form.errors))

    def test_clean_recent_previous(self):
        Caffeine.objects.create(
            user=self.user, ctype=DRINK_TYPES.coffee,
            date=timezone.now() - timedelta(
                minutes=settings.MINIMUM_DRINK_DISTANCE - 1))
        now = timezone.now()
        form = SubmitCaffeineForm(
            self.user, DRINK_TYPES.coffee,
            data={'date': now.date(), 'time': now.time()}
        )
        self.assertFalse(form.is_valid())
        form_errors = form.non_field_errors()
        self.assertEqual(len(form_errors), 1)
        self.assertRegexpMatches(
            form_errors[0],
            r'^Your last %(drink)s was less than %(minutes)d minutes ago' % {
                'drink': DRINK_TYPES[DRINK_TYPES.coffee],
                'minutes': settings.MINIMUM_DRINK_DISTANCE
            })
