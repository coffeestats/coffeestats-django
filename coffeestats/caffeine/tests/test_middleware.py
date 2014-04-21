from django.core.urlresolvers import reverse
from django.http import HttpRequest, HttpResponseRedirect
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from caffeine.middleware import EnforceTimezoneMiddleware


User = get_user_model()


class TestEnforceTimezoneMiddleware(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.middleware = EnforceTimezoneMiddleware()

    def test_anonymous_user(self):
        request = HttpRequest()
        request.user = AnonymousUser()
        self.assertIsNone(self.middleware.process_request(request))

    def test_user_with_no_timezone_set(self):
        request = HttpRequest()
        request.user = self.user
        response = self.middleware.process_request(request)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(
            response['Location'].startswith(reverse('selecttimezone')))
        self.assertIn(
            '?next=', response['Location'])

    def test_no_redirect_loop(self):
        request = HttpRequest()
        request.user = self.user
        request.path = reverse('selecttimezone')
        self.assertIsNone(self.middleware.process_request(request))

    def test_no_redirect_if_user_has_timezone(self):
        self.user.timezone = 'GMT'
        request = HttpRequest()
        request.user = self.user
        self.assertIsNone(self.middleware.process_request(request))
