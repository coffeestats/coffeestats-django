from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse

from caffeine.context_processors import NavItem, SubNav, SubNavItem, mainnav

User = get_user_model()


class TestNavItem(TestCase):
    def test_navitem_active(self):
        request = HttpRequest()
        request.path = "/test"
        navitem = NavItem(request, "/test", None, None)
        self.assertTrue(navitem.is_active())


class TestSubNav(TestCase):
    def test_subnav_active(self):
        request = HttpRequest()
        request.path = "/test"
        subnav = SubNav(
            request, "Test", None, (NavItem(request, "/test", None, None),), None
        )
        self.assertTrue(subnav.is_active())


class TestMainNavContextProcessor(TestCase):
    def test_no_navitems_for_anonymous(self):
        request = HttpRequest()
        request.user = AnonymousUser()
        result = mainnav(request)
        self.assertEqual(result, {})

    def test_navitems_for_authenticated(self):
        user = User.objects.create_user("test", "test")
        request = HttpRequest()
        request.user = user
        result = mainnav(request)
        self.assertIsInstance(result, dict)
        self.assertIn("navitems", result)
        self.assertEqual(len(result["navitems"]), 4)
        for item in result["navitems"][0:3]:
            self.assertIsInstance(item, NavItem)
        self.assertIsInstance(result["navitems"][3], SubNav)
        self.assertEqual(len(result["navitems"][3].children), 3)
        for subitem in result["navitems"][3].children:
            self.assertIsInstance(subitem, SubNavItem)
        adminurl = reverse("admin:index")
        self.assertFalse(
            any([adminurl == subitem.url for subitem in result["navitems"][3].children])
        )

    def test_navitems_for_staff(self):
        user = User.objects.create_user("staffmember", "test")
        user.is_staff = True
        request = HttpRequest()
        request.user = user
        result = mainnav(request)
        self.assertIsInstance(result, dict)
        self.assertIn("navitems", result)
        self.assertEqual(len(result["navitems"]), 4)
        for item in result["navitems"][0:3]:
            self.assertIsInstance(item, NavItem)
        self.assertIsInstance(result["navitems"][3], SubNav)
        self.assertEqual(len(result["navitems"][3].children), 4)
        for subitem in result["navitems"][3].children:
            self.assertIsInstance(subitem, SubNavItem)
        adminurl = reverse("admin:index")
        self.assertTrue(
            any([adminurl == subitem.url for subitem in result["navitems"][3].children])
        )
