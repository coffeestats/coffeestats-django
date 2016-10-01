from django.test import SimpleTestCase

from caffeine_oauth2.models import CoffeestatsApplication
from caffeine_oauth2.views import CoffeestatsApplicationRegistration


class CoffeestatsApplicationRegistrationTest(SimpleTestCase):
    def test_get_form_class(self):
        view = CoffeestatsApplicationRegistration()
        form_class = view.get_form_class()
        self.assertIsNotNone(form_class)
        self.assertEqual(form_class.Meta.model, CoffeestatsApplication)


# TODO: add tests for the other views
