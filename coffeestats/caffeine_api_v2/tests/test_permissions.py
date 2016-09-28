from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import SimpleTestCase
from mock import Mock

from caffeine_api_v2.permissions import (
    IsOwnerOrReadOnly, IsOwnCaffeineOrReadOnly
)

User = get_user_model()


class IsOwnerOrReadOnlyTest(SimpleTestCase):
    def setUp(self):
        self.subject = IsOwnerOrReadOnly()

    def test_has_object_permission_safe(self):
        request = HttpRequest()
        for meth in ['GET', 'HEAD', 'OPTIONS']:
            request.method = meth
            self.assertTrue(
                self.subject.has_object_permission(request, None, None))

    def test_has_object_permission_same_user(self):
        request = HttpRequest()
        request.method = 'POST'
        dummyuser = User(username='User')
        request.user = dummyuser
        model = Mock(user=dummyuser)
        self.assertTrue(
            self.subject.has_object_permission(request, None, model))

    def test_has_object_permission_other_user(self):
        request = HttpRequest()
        request.method = 'POST'
        request.user = User(username='User')
        model = Mock(user=User(username='Other'))
        self.assertFalse(
            self.subject.has_object_permission(request, None, model))


class IsOwnCaffeineOrReadOnlyTest(SimpleTestCase):
    def setUp(self):
        self.subject = IsOwnCaffeineOrReadOnly()

    def test_has_permission_safe(self):
        request = HttpRequest()
        for meth in ['GET', 'HEAD', 'OPTIONS']:
            request.method = meth
            self.assertTrue(
                self.subject.has_permission(request, None))

    def test_own_caffeine(self):
        request = HttpRequest()
        request.method = 'POST'
        owner_user = User(username='User')
        request.user = owner_user
        view = Mock(view_owner=owner_user)
        self.assertTrue(self.subject.has_permission(request, view))

    def test_other_caffeine(self):
        request = HttpRequest()
        request.method = 'POST'
        owner_user = User(username='User')
        request.user = User(username='Other')
        view = Mock(view_owner=owner_user)
        self.assertFalse(self.subject.has_permission(request, view))
