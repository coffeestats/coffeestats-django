import json
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from caffeine.models import (
    Caffeine,
    DRINK_TYPES,
)
from caffeine_api_v1.views import (
    API_ERROR_AUTH_REQUIRED,
    API_ERROR_FUTURE_DATETIME,
    API_ERROR_INVALID_BEVERAGE,
    API_ERROR_INVALID_CREDENTIALS,
    API_ERROR_INVALID_DATETIME,
    API_ERROR_MISSING_PARAM_BEVERAGE,
    API_ERROR_MISSING_PARAM_TIME,
    API_ERROR_NO_TOKEN,
    API_ERROR_NO_USERNAME,
    API_WARNING_TIMEZONE_NOT_SET,
    api_token_required,
)
from core.utils import json_response

User = get_user_model()

_TEST_PASSWORD = 'test1234'


class ApiTokenRequiredTest(TestCase):

    def setUp(self):
        def testfun(_, messages, userinfo):
            messages['success'] = True
            return {'messages': messages,
                    'user': userinfo.username}

        self.user = User.objects.create_user(
            'testuser', 'test@example.org', password=_TEST_PASSWORD,
            token='testtoken', is_active=True)
        self.wrapped = api_token_required(json_response(testfun))
        self.request = HttpRequest()
        self.request.method = 'POST'

    def test_no_username(self):
        self.request.POST.update({'t': self.user.token})
        response = self.wrapped(self.request)
        self.assertIsInstance(response, HttpResponseForbidden)
        self.assertEqual(response['content-type'], 'text/json')
        messages = json.loads(response.content)
        self.assertIn('error', messages)
        self.assertIn(API_ERROR_NO_USERNAME, messages['error'])
        self.assertIn(API_ERROR_AUTH_REQUIRED, messages['error'])
        self.assertFalse(messages['success'])

    def test_no_token(self):
        self.request.POST.update({'u': self.user.username})
        response = self.wrapped(self.request)
        self.assertIsInstance(response, HttpResponseForbidden)
        self.assertEqual(response['content-type'], 'text/json')
        messages = json.loads(response.content)
        self.assertIn('error', messages)
        self.assertIn(API_ERROR_NO_TOKEN, messages['error'])
        self.assertIn(API_ERROR_AUTH_REQUIRED, messages['error'])
        self.assertFalse(messages['success'])

    def test_invalid_credentials(self):
        self.request.POST.update({
            'u': 'wronguser',
            't': 'brokentoken',
        })
        response = self.wrapped(self.request)
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response['content-type'], 'text/json')
        messages = json.loads(response.content)
        self.assertIn('error', messages)
        self.assertEqual(messages['error'], [API_ERROR_INVALID_CREDENTIALS])
        self.assertFalse(messages['success'])

    def test_valid_user_without_timezone(self):
        self.request.POST.update({
            'u': self.user.username,
            't': self.user.token,
        })
        response = self.wrapped(self.request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response['content-type'], 'text/json')
        responsedata = json.loads(response.content)
        self.assertIn('user', responsedata)
        self.assertEqual(responsedata['user'], self.user.username)
        self.assertIn('messages', responsedata)
        self.assertEqual(
            responsedata['messages'],
            {'warning': [API_WARNING_TIMEZONE_NOT_SET],
             'success': True}
        )

    def test_valid_user_with_timezone(self):
        self.user.timezone = 'Europe/Berlin'
        self.user.save()
        self.request.POST.update({
            'u': self.user.username,
            't': self.user.token,
        })
        response = self.wrapped(self.request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response['content-type'], 'text/json')
        responsedata = json.loads(response.content)
        self.assertIn('user', responsedata)
        self.assertEqual(responsedata['user'], self.user.username)
        self.assertIn('messages', responsedata)
        self.assertEqual(
            responsedata['messages'],
            {'success': True}
        )


class RandomUsersTest(TestCase):

    def setUp(self):
        super(RandomUsersTest, self).setUp()
        self.user = User.objects.create_user(
            'testuser', 'test@example.org', password=_TEST_PASSWORD,
            token='testtoken', is_active=True)
        self.user.timezone = 'Europe/Berlin'
        self.user.save()

    def test_requires_authentication(self):
        myurl = reverse('apiv1:random_users')
        response = self.client.post(myurl)
        self.assertEqual(response.status_code, 403)

    def test_missing_count_yields_five_users(self):
        for num in range(10):
            User.objects.create_user(
                'test{}'.format(num + 1), 'test{}@example.org'.format(num + 1),
                token='testtoken{}'.format(num + 1),
                date_joined=timezone.now() - timedelta(days=num),
                is_active=True)

        response = self.client.post(reverse('apiv1:random_users'), data={
            'u': self.user.username,
            't': self.user.token,
        })
        self.assertEqual(response['content-type'], 'text/json')
        data = json.loads(response.content)
        self.assertEqual(len(data), 5)

    def test_get_random_users(self):
        for num in range(10):
            User.objects.create_user(
                'test{}'.format(num + 1), 'test{}@example.org'.format(num + 1),
                token='testtoken{}'.format(num + 1),
                date_joined=timezone.now() - timedelta(days=num),
                is_active=True)

        response = self.client.post(
            reverse('apiv1:random_users'),
            data={
                'u': self.user.username,
                't': self.user.token,
                'count': 4,
            }
        )
        self.assertEqual(response['content-type'], 'text/json')
        data = json.loads(response.content)
        self.assertEqual(len(data), 4)
        for item in data:
            self.assertTrue(item['username'].startswith('test'))
            for key in (
                    'username', 'name', 'location', 'profile', 'coffees', 'mate'
            ):
                self.assertIn(key, item)


class AddDrinkTest(TestCase):

    def setUp(self):
        super(AddDrinkTest, self).setUp()
        self.user = User.objects.create_user(
            'testuser', 'test@example.org', password=_TEST_PASSWORD,
            token='testtoken', is_active=True)
        self.user.timezone = 'Europe/Berlin'
        self.user.save()
        self.url = reverse('apiv1:add_drink')

    def test_get_not_supported(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_beverage_required(self):
        response = self.client.post(self.url, data={
            'u': self.user.username, 't': self.user.token,
        })
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response['content-type'], 'text/json')
        messages = json.loads(response.content)
        self.assertIn('error', messages)
        self.assertIn(API_ERROR_MISSING_PARAM_BEVERAGE, messages['error'])
        self.assertFalse(messages['success'])

    def test_invalid_beverage(self):
        response = self.client.post(self.url, data={
            'u': self.user.username, 't': self.user.token,
            'beverage': 'water',
        })
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response['content-type'], 'text/json')
        messages = json.loads(response.content)
        self.assertIn('error', messages)
        self.assertIn(API_ERROR_INVALID_BEVERAGE, messages['error'])
        self.assertFalse(messages['success'])

    def test_time_required(self):
        response = self.client.post(self.url, data={
            'u': self.user.username, 't': self.user.token,
        })
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response['content-type'], 'text/json')
        messages = json.loads(response.content)
        self.assertIn('error', messages)
        self.assertIn(API_ERROR_MISSING_PARAM_TIME, messages['error'])
        self.assertFalse(messages['success'])

    def test_time_parsing_invalid(self):
        response = self.client.post(self.url, data={
            'u': self.user.username, 't': self.user.token,
            'beverage': 'coffee', 'time': 'invalid',
        })
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response['content-type'], 'text/json')
        messages = json.loads(response.content)
        self.assertIn('error', messages)
        self.assertIn(API_ERROR_INVALID_DATETIME, messages['error'])
        self.assertFalse(messages['success'])

    def test_time_parsing_no_seconds(self):
        response = self.client.post(self.url, data={
            'u': self.user.username, 't': self.user.token,
            'beverage': 'coffee',
            'time': timezone.now().strftime('%Y-%m-%d %H:%M'),
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'text/json')
        messages = json.loads(response.content)
        self.assertNotIn('error', messages)
        self.assertTrue(messages['success'])
        self.assertEqual(len(Caffeine.objects.all()), 1)

    def test_future_time(self):
        response = self.client.post(self.url, data={
            'u': self.user.username, 't': self.user.token,
            'beverage': 'coffee',
            'time': (timezone.now() +
                     timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
        })
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response['content-type'], 'text/json')
        messages = json.loads(response.content)
        self.assertIn('error', messages)
        self.assertIn(API_ERROR_FUTURE_DATETIME, messages['error'])
        self.assertFalse(messages['success'])

    def test_form_validation_failure(self):
        Caffeine.objects.create(
            ctype=DRINK_TYPES.coffee, user=self.user,
            date=timezone.now())
        response = self.client.post(self.url, data={
            'u': self.user.username, 't': self.user.token,
            'beverage': 'coffee',
            'time': timezone.now().strftime('%Y-%m-%d %H:%M'),
        })
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response['content-type'], 'text/json')
        messages = json.loads(response.content)
        self.assertIn('error', messages)
        self.assertFalse(messages['success'])

    def test_submit_older_caffeine(self):
        Caffeine.objects.create(
            ctype=DRINK_TYPES.coffee, user=self.user,
            date=timezone.now())
        before = timezone.now() - timedelta(
            minutes=settings.MINIMUM_DRINK_DISTANCE + 1)
        response = self.client.post(self.url, data={
            'u': self.user.username, 't': self.user.token,
            'beverage': 'coffee',
            'time': before.strftime('%Y-%m-%d %H:%M'),
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'text/json')
        messages = json.loads(response.content)
        self.assertNotIn('error', messages)
        self.assertTrue(messages['success'])
        self.assertEqual(len(Caffeine.objects.all()), 2)

    def test_form_validation_close_before_time(self):
        Caffeine.objects.create(
            ctype=DRINK_TYPES.coffee, user=self.user,
            date=timezone.now())
        close_before = timezone.now() - timedelta(
            minutes=settings.MINIMUM_DRINK_DISTANCE - 1)
        response = self.client.post(self.url, data={
            'u': self.user.username, 't': self.user.token,
            'beverage': 'coffee',
            'time': close_before.strftime('%Y-%m-%d %H:%M'),
        })
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response['content-type'], 'text/json')
        messages = json.loads(response.content)
        self.assertIn('error', messages)
        self.assertFalse(messages['success'])
