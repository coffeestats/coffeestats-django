from unittest.mock import Mock

from django.urls import reverse
from django.http import HttpRequest, HttpResponseRedirect
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from caffeine.middleware import EnforceTimezoneMiddleware


User = get_user_model()


class TestEnforceTimezoneMiddleware(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.org')
        self.response_mock = Mock()
        self.middleware = EnforceTimezoneMiddleware(self.get_response)

    # noinspection PyUnusedLocal
    def get_response(self, request):
        return self.response_mock

    def test_anonymous_user(self):
        request = HttpRequest()
        request.user = AnonymousUser()
        response = self.middleware(request)
        self.assertIs(response, self.response_mock)

    def test_user_with_no_timezone_set(self):
        request = HttpRequest()
        request.user = self.user
        response = self.middleware(request)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(
            response['Location'].startswith(reverse('select_timezone')))
        self.assertIn(
            '?next=', response['Location'])

    def test_no_redirect_loop(self):
        request = HttpRequest()
        request.user = self.user
        request.path = reverse('select_timezone')
        response = self.middleware(request)
        self.assertIs(response, self.response_mock)

    def test_no_redirect_if_user_has_timezone(self):
        self.user.timezone = 'GMT'
        request = HttpRequest()
        request.user = self.user
        response = self.middleware(request)
        self.assertIs(response, self.response_mock)
