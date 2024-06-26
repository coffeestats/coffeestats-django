import json
from datetime import timedelta
from unittest.mock import patch

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from caffeine.forms import (
    CoffeestatsRegistrationForm,
    EMPTY_TIMEZONE_ERROR,
    SettingsForm,
)
from caffeine.models import ACTION_TYPES, Action, Caffeine, DRINK_TYPES
from caffeine.views import (
    ACTIVATION_SUCCESS_MESSAGE,
    CaffeineRegistrationView,
    DELETE_ACCOUNT_MESSAGE,
    DELETE_CAFFEINE_SUCCESS_MESSAGE,
    EMAIL_CHANGE_SUCCESS_MESSAGE,
    EXPORT_SUCCESS_MESSAGE,
    REGISTRATION_MAILINFO_MESSAGE,
    REGISTRATION_SUCCESS_MESSAGE,
    SELECT_TIMEZONE_SUCCESS_MESSAGE,
    SETTINGS_EMAIL_CHANGE_MESSAGE,
    SETTINGS_PASSWORD_CHANGE_SUCCESS,
    SETTINGS_SUCCESS_MESSAGE,
    SUBMIT_CAFFEINE_SUCCESS_MESSAGE,
)

User = get_user_model()

_TEST_PASSWORD = "test1234"


class CaffeineViewTest(TestCase):
    def _create_testuser(self, is_active=True):
        user = User.objects.create_user(
            "testuser",
            "test@bla.com",
            password=_TEST_PASSWORD,
            token="testfoo",
            is_active=is_active,
        )
        user.timezone = "Europe/Berlin"
        user.save()
        return user

    def _do_login(self, user=None, password=_TEST_PASSWORD):
        if user is None:
            user = self._create_testuser()
        return self.client.login(username=user.username, password=password)


class MessagesTestMixin(object):
    def assertMessageCount(self, response, expected_num):
        self.assertEqual(len(response.context["messages"]), expected_num)

    def assertMessageContains(self, response, text, level=None):
        response_messages = response.context["messages"]
        matches = [m for m in response_messages if text in m.message]

        if len(matches) == 1:
            msg = matches[0]
            if level is not None and msg.level != level:
                self.fail(
                    "There was one matching message but different"
                    " level: %s != %s" % (msg.level, level)
                )
        elif len(matches) == 0:
            messages_str = ", ".join('"%s"' % m for m in response_messages)
            self.fail(
                'No message contained text "%s", messages were: %s'
                % (text, messages_str)
            )
        else:
            self.fail(
                'Multiple messages contained text "%s": %s'
                % (text, ", ".join(('"%s"' % m) for m in matches))
            )


class AboutViewTest(CaffeineViewTest):
    def test_redirects_to_login(self):
        response = self.client.get("/about/")
        self.assertRedirects(response, "/auth/login/?next=/about/")

    def test_renders_about_template(self):
        self.assertTrue(self._do_login(), "login failed")
        response = self.client.get("/about/")
        self.assertTemplateUsed(response, "about.html")


class ExploreViewTest(CaffeineViewTest):
    def test_redirects_to_login(self):
        response = self.client.get("/explore/")
        self.assertRedirects(response, "/auth/login/?next=/explore/")

    def test_renders_explore_template(self):
        self.assertTrue(self._do_login(), "login failed")
        response = self.client.get("/explore/")
        self.assertTemplateUsed(response, "explore.html")

    def test_context_items(self):
        self.assertTrue(self._do_login(), "login failed")
        response = self.client.get("/explore/")
        for item in (
            "activities",
            "users",
            "topcoffee",
            "topcoffeeavg",
            "topmate",
            "topmateavg",
            "topcoffeerecent",
            "topmaterecent",
            "recentlyjoined",
            "longestjoined",
        ):
            self.assertIn(item, response.context)


class ExportActivityView(MessagesTestMixin, CaffeineViewTest):
    def test_redirects_to_login(self):
        response = self.client.get("/activity/export/")
        self.assertRedirects(response, "/auth/login/?next=/activity/export/")

    def test_sends_csv_mail(self):
        self.assertTrue(self._do_login(), "login failed")
        response = self.client.get("/activity/export/", follow=True)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Your caffeine records")
        self.assertMessageCount(response, 1)
        self.assertMessageContains(response, EXPORT_SUCCESS_MESSAGE, messages.INFO)


class DeleteAccountViewTest(MessagesTestMixin, CaffeineViewTest):
    def test_redirects_to_login(self):
        response = self.client.get("/deletemyaccount/")
        self.assertRedirects(response, "/auth/login/?next=/deletemyaccount/")

    def test_renders_delete_confirmation_template(self):
        self.assertTrue(self._do_login(), "login failed")
        response = self.client.get("/deletemyaccount/")
        self.assertTemplateUsed(response, "caffeine/user_confirm_delete.html")
        self.assertIn("user", response.context)

    def test_delete(self):
        self.assertTrue(self._do_login(), "login failed")
        response = self.client.post("/deletemyaccount/", follow=True)
        self.assertMessageCount(response, 1)
        self.assertMessageContains(response, DELETE_ACCOUNT_MESSAGE, messages.INFO)
        self.assertFalse(
            self.client.login(username="testuser", password=_TEST_PASSWORD)
        )


class ImprintViewTest(TestCase):
    def test_renders_imprint_template(self):
        response = self.client.get("/imprint/")
        self.assertTemplateUsed(response, "imprint.html")


class IndexViewTest(CaffeineViewTest):
    def test_renders_index_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "index.html")


class OverallViewTest(CaffeineViewTest):
    def test_renders_overall_template(self):
        response = self.client.get("/overall/")
        self.assertTemplateUsed(response, "overall.html")

    def test_context_items(self):
        response = self.client.get("/overall/")
        for item in (
            "coffees",
            "mate",
            "todaydata",
            "monthdata",
            "yeardata",
            "byhourdata",
            "byweekdaydata",
        ):
            self.assertIn(item, response.context)


class ProfileViewsTest(CaffeineViewTest):
    """
    Test case for both ProfileView and PublicProfileView.

    """

    def test_redirect_for_anonymous(self):
        response = self.client.get("/profile/")
        self.assertRedirects(response, "/auth/login/?next=/profile/")

    def test_notfound_for_missing_user(self):
        response = self.client.get("/profile/testuser/")
        self.assertEqual(response.status_code, 404)

    def test_redirects_to_public_for_parameter(self):
        self._create_testuser()
        response = self.client.get("/profile/?u=testuser")
        self.assertRedirects(response, "/profile/testuser/")

    def test_renders_profile_template_for_ownprofile(self):
        self.assertTrue(self._do_login(), "login failed")
        response = self.client.get("/profile/")
        self.assertTemplateUsed(response, "profile.html")

    def test_renders_profile_template_for_parameter(self):
        self._create_testuser()
        response = self.client.get("/profile/testuser/")
        self.assertTemplateUsed(response, "profile.html")

    def test_context_items_public(self):
        self._create_testuser()
        response = self.client.get("/profile/testuser/")
        for item in (
            "byhourdata",
            "byweekdaydata",
            "coffees",
            "mate",
            "monthdata",
            "ownprofile",
            "profileuser",
            "todaydata",
            "yeardata",
        ):
            self.assertIn(item, response.context)
        self.assertNotIn("entries", response.context)
        self.assertFalse(response.context["ownprofile"])

    def test_context_items_own(self):
        self.assertTrue(self._do_login(), "login failed")
        response = self.client.get("/profile/")
        for item in (
            "byhourdata",
            "byweekdaydata",
            "coffees",
            "mate",
            "monthdata",
            "ownprofile",
            "profileuser",
            "todaydata",
            "yeardata",
            "entries",
        ):
            self.assertIn(item, response.context)
        self.assertTrue(response.context["ownprofile"])


class CaffeineActivationViewTest(MessagesTestMixin, CaffeineViewTest):
    def test_redirects_to_home(self):
        user = self._create_testuser(is_active=False)
        activation_key = CaffeineRegistrationView().get_activation_key(user)
        response = self.client.get(
            "/auth/activate/{}/".format(activation_key), follow=True
        )
        self.assertRedirects(response, "/")
        self.assertIsNotNone(user.token)
        self.assertNotEqual(user.token, "")

    def test_activation_success_message(self):
        user = self._create_testuser(is_active=False)
        activation_key = CaffeineRegistrationView().get_activation_key(user)
        response = self.client.get(
            "/auth/activate/{}/".format(activation_key), follow=True
        )
        self.assertMessageCount(response, 1)
        self.assertMessageContains(response, ACTIVATION_SUCCESS_MESSAGE)


class CaffeineRegistrationViewTest(MessagesTestMixin, CaffeineViewTest):
    TEST_POST_DATA = {
        "username": "testuser",
        "email": "test@bla.com",
        "password1": _TEST_PASSWORD,
        "password2": _TEST_PASSWORD,
        "firstname": "Test",
        "lastname": "User",
        "location": "Testino",
    }

    def test_get_renders_registration_template(self):
        response = self.client.get("/auth/register/")
        self.assertTemplateUsed(response, "django_registration/registration_form.html")

    def test_get_context_has_form(self):
        response = self.client.get("/auth/register/")
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], CoffeestatsRegistrationForm)

    def test_empty_post_renders_errors(self):
        response = self.client.post("/auth/register/", data={})
        self.assertIn(b"errorlist", response.content)

    def test_successful_post_creates_inactive_user(self):
        self.client.post("/auth/register/", data=self.TEST_POST_DATA)
        user = User.objects.get(username=self.TEST_POST_DATA["username"])
        self.assertFalse(user.is_active)
        self.assertEqual(user.first_name, self.TEST_POST_DATA["firstname"])
        self.assertEqual(user.last_name, self.TEST_POST_DATA["lastname"])
        self.assertEqual(user.location, self.TEST_POST_DATA["location"])

    def test_successful_post_sends_email(self):
        self.client.post("/auth/register/", data=self.TEST_POST_DATA)
        self.assertEqual(len(mail.outbox), 1)
        first_mail = mail.outbox[0]
        self.assertEqual(first_mail.to, [self.TEST_POST_DATA["email"]])
        self.assertIn(
            reverse(
                "django_registration_activate", kwargs={"activation_key": "abc"}
            ).rsplit("/", maxsplit=2)[0],
            first_mail.body,
        )

    def test_successful_post_creates_messages(self):
        response = self.client.post(
            "/auth/register/", data=self.TEST_POST_DATA, follow=True
        )
        self.assertMessageCount(response, 2)
        self.assertMessageContains(
            response, REGISTRATION_SUCCESS_MESSAGE, messages.SUCCESS
        )
        self.assertMessageContains(
            response, REGISTRATION_MAILINFO_MESSAGE, messages.INFO
        )

    def test_redirects_to_home(self):
        response = self.client.post(
            "/auth/register/", data=self.TEST_POST_DATA, follow=True
        )
        self.assertRedirects(response, "/")


class RegistrationClosedViewTest(CaffeineViewTest):
    def setUp(self):
        settings.REGISTRATION_OPEN = False
        super(RegistrationClosedViewTest, self).setUp()

    def tearDown(self):
        super(RegistrationClosedViewTest, self).tearDown()
        settings.REGISTRATION_OPEN = True

    def test_registration_redirects_to_registration_closed(self):
        response = self.client.get("/auth/register/")
        self.assertRedirects(response, "/auth/register/closed")

    def test_renders_registration_closed_template(self):
        response = self.client.get("/auth/register/closed")
        self.assertTemplateUsed(
            response, "django_registration/registration_closed.html"
        )


class SettingsViewTest(MessagesTestMixin, CaffeineViewTest):
    def test_redirects_to_login(self):
        response = self.client.get("/settings/")
        self.assertRedirects(response, "/auth/login/?next=/settings/")

    def test_renders_settings_templates(self):
        self.assertTrue(self._do_login(), "login failed")
        response = self.client.get("/settings/")
        self.assertTemplateUsed(response, "settings.html")

    def test_uses_settings_form(self):
        self.assertTrue(self._do_login(), "login failed")
        response = self.client.get("/settings/")
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], SettingsForm)

    def test_form_user_is_login_user(self):
        login_user = self._create_testuser()
        self.assertTrue(
            self.client.login(username=login_user.username, password=_TEST_PASSWORD),
            "login failed",
        )
        response = self.client.get("/settings/")
        self.assertEqual(response.context["form"].instance, login_user)

    def test_email_change_sends_email(self):
        login_user = self._create_testuser()
        self.assertTrue(
            self.client.login(username=login_user.username, password=_TEST_PASSWORD),
            "login failed",
        )
        self.client.post(
            "/settings/",
            data={
                "email": "test@example.org",
            },
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], login_user.email)
        self.assertIn("test@example.org", mail.outbox[0].body)

    def test_email_change_message(self):
        self.assertTrue(self._do_login(), "login failed")
        response = self.client.post(
            "/settings/",
            data={
                "email": "test@example.org",
            },
            follow=True,
        )
        self.assertMessageCount(response, 2)
        self.assertMessageContains(response, SETTINGS_SUCCESS_MESSAGE, messages.SUCCESS)
        self.assertMessageContains(
            response, SETTINGS_EMAIL_CHANGE_MESSAGE, messages.INFO
        )

    def test_password_change_message(self):
        login_user = self._create_testuser()
        self.assertTrue(
            self.client.login(username=login_user.username, password=_TEST_PASSWORD),
            "login failed",
        )
        response = self.client.post(
            "/settings/",
            data={
                "email": login_user.email,
                "password1": "test5432",
                "password2": "test5432",
            },
            follow=True,
        )
        self.assertMessageCount(response, 2)
        self.assertMessageContains(response, SETTINGS_SUCCESS_MESSAGE, messages.SUCCESS)
        self.assertMessageContains(
            response, SETTINGS_PASSWORD_CHANGE_SUCCESS, messages.SUCCESS
        )


class ConfirmActionViewTest(MessagesTestMixin, CaffeineViewTest):
    def _create_action_confirm_request(self, data="bla@fasel.com"):
        user = self._create_testuser()
        action = Action.objects.create_action(user, ACTION_TYPES.change_email, data, 1)
        response = self.client.get(
            "/action/confirm/{}/".format(action.code), follow=True
        )
        return user, action, response

    def test_redirects_to_home(self):
        _, _, response = self._create_action_confirm_request()
        self.assertRedirects(response, "/")

    def test_action_is_deleted_after_access(self):
        _, action, _ = self._create_action_confirm_request()
        self.assertEqual(len(Action.objects.all()), 0)

    def test_user_email_changed_after_access(self):
        user, _, _ = self._create_action_confirm_request("bla@fasel.com")
        self.assertEqual(User.objects.get(pk=user.pk).email, "bla@fasel.com")

    def test_email_change_message(self):
        _, _, response = self._create_action_confirm_request()
        self.assertMessageCount(response, 1)
        self.assertMessageContains(response, EMAIL_CHANGE_SUCCESS_MESSAGE)

    @patch("caffeine.views.ACTION_TYPES")
    def test_redirects_to_home_for_other_action(self, atypes_mock):
        atypes_mock.change_email = "fake"
        user = self._create_testuser()
        action = Action.objects.create_action(
            user, ACTION_TYPES.change_email, "foo@bar.com", 1
        )
        response = self.client.get(
            "/action/confirm/{}/".format(action.code), follow=True
        )
        self.assertRedirects(response, "/")


class OnTheRunViewTest(CaffeineViewTest):
    def test_renders_ontherun_template(self):
        user = self._create_testuser()
        response = self.client.get("/ontherun/{}/{}/".format(user.username, user.token))
        self.assertTemplateUsed(response, "ontherun.html")

    def test_404_for_wrong_user(self):
        user = self._create_testuser()
        response = self.client.get("/ontherun/wronguser/{}/".format(user.token))
        self.assertEqual(response.status_code, 404)

    def test_404_for_wrong_token(self):
        user = self._create_testuser()
        response = self.client.get("/ontherun/{}/wrongpass/".format(user.username))
        self.assertEqual(response.status_code, 404)

    def test_contains_submit_caffeine_links(self):
        user = self._create_testuser()
        response = self.client.get("/ontherun/{}/{}/".format(user.username, user.token))
        self.assertIn(
            "/coffee/submit/{}/{}/".format(user.username, user.token).encode("utf8"),
            response.content,
        )
        self.assertIn(
            "/mate/submit/{}/{}/".format(user.username, user.token).encode("utf8"),
            response.content,
        )


class OnTheRunOldViewTest(CaffeineViewTest):
    def test_redirects_to_ontherun(self):
        user = self._create_testuser()
        response = self.client.get(
            "/ontherun/?u={}&t={}".format(user.username, user.token)
        )
        self.assertRedirects(
            response,
            "/ontherun/{}/{}/".format(user.username, user.token),
            status_code=301,
        )

    def test_404_for_wrong_user(self):
        user = self._create_testuser()
        response = self.client.get("/ontherun/?u=wronguser&t={}".format(user.token))
        self.assertEqual(response.status_code, 404)

    def test_404_for_wrong_token(self):
        user = self._create_testuser()
        response = self.client.get("/ontherun/?u={}&t=wrongtoken".format(user.username))
        self.assertEqual(response.status_code, 404)


class SubmitCaffeineViewTest(MessagesTestMixin, CaffeineViewTest):
    def test_redirects_to_login(self):
        response = self.client.post("/coffee/submit/")
        self.assertRedirects(response, "/auth/login/?next=/coffee/submit/")

    def test_does_not_support_get(self):
        self.assertTrue(self._do_login(), "login failed")
        response = self.client.get("/coffee/submit/")
        self.assertEqual(response.status_code, 405)

    def test_redirects_to_profile(self):
        self.assertTrue(self._do_login(), "login failed")
        now = timezone.now()
        response = self.client.post(
            "/coffee/submit/", data={"date": now.date(), "time": now.time()}
        )
        self.assertRedirects(response, "/profile/")

    def test_success_message(self):
        self.assertTrue(self._do_login(), "login failed")
        now = timezone.now()
        response = self.client.post(
            "/coffee/submit/",
            data={"date": now.date(), "time": now.time()},
            follow=True,
        )
        self.assertMessageCount(response, 1)
        coffee = Caffeine.objects.all()[0]
        self.assertMessageContains(
            response,
            SUBMIT_CAFFEINE_SUCCESS_MESSAGE
            % {
                "caffeine": coffee,
            },
            messages.SUCCESS,
        )

    def test_error_message(self):
        user = self._create_testuser()
        self.assertTrue(self._do_login(user), "login failed")
        Caffeine.objects.create(
            ctype=DRINK_TYPES.coffee,
            user=user,
            date=timezone.now() - timedelta(minutes=3),
        )
        now = timezone.now()
        response = self.client.post(
            "/coffee/submit/",
            data={"date": now.date(), "time": now.time()},
            follow=True,
        )
        self.assertMessageCount(response, 1)
        self.assertMessageContains(response, "", messages.ERROR)


class SubmitCaffeineOnTheRunView(MessagesTestMixin, CaffeineViewTest):
    def test_does_not_support_get(self):
        user = self._create_testuser()
        response = self.client.get(
            "/coffee/submit/{}/{}/".format(user.username, user.token)
        )
        self.assertEqual(response.status_code, 405)

    def test_redirects_to_ontherun(self):
        user = self._create_testuser()
        now = timezone.now()
        response = self.client.post(
            "/coffee/submit/{}/{}/".format(user.username, user.token),
            data={"date": now.date(), "time": now.time()},
        )
        self.assertRedirects(
            response, "/ontherun/{}/{}/".format(user.username, user.token)
        )

    def test_success_message(self):
        user = self._create_testuser()
        now = timezone.now()
        response = self.client.post(
            "/coffee/submit/{}/{}/".format(user.username, user.token),
            data={"date": now.date(), "time": now.time()},
            follow=True,
        )
        self.assertMessageCount(response, 1)
        coffee = Caffeine.objects.all()[0]
        self.assertMessageContains(
            response,
            SUBMIT_CAFFEINE_SUCCESS_MESSAGE
            % {
                "caffeine": coffee,
            },
            messages.SUCCESS,
        )

    def test_error_message(self):
        user = self._create_testuser()
        Caffeine.objects.create(
            ctype=DRINK_TYPES.coffee,
            user=user,
            date=timezone.now() - timedelta(minutes=3),
        )
        now = timezone.now()
        response = self.client.post(
            "/coffee/submit/{}/{}/".format(user.username, user.token),
            data={"date": now.date(), "time": now.time()},
            follow=True,
        )
        self.assertMessageCount(response, 1)
        self.assertMessageContains(response, "", messages.ERROR)


class DeleteCaffeineViewTest(MessagesTestMixin, CaffeineViewTest):
    def setUp(self):
        super(DeleteCaffeineViewTest, self).setUp()
        self.user = self._create_testuser()
        self.caffeine = Caffeine.objects.create(
            ctype=DRINK_TYPES.coffee, date=timezone.now(), user=self.user
        )
        self.delete_url = "/delete/{}/".format(self.caffeine.id)

    def test_redirects_to_login(self):
        response = self.client.get(self.delete_url)
        self.assertRedirects(response, "/auth/login/?next={}".format(self.delete_url))

    def test_render_delete_caffeine_template(self):
        self.assertTrue(self._do_login(self.user), "login failed")
        response = self.client.get(self.delete_url)
        self.assertTemplateUsed(response, "caffeine/caffeine_confirm_delete.html")

    def test_404_for_not_existing_caffeine(self):
        self.assertTrue(self._do_login(self.user), "login failed")
        response = self.client.post("/delete/{}/".format(self.caffeine.id + 1))
        self.assertEqual(response.status_code, 404)

    def test_redirects_to_profile_after_delete(self):
        self.assertTrue(self._do_login(self.user), "login failed")
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, "/profile/")

    def test_can_delete_own_caffeine(self):
        self.assertTrue(self._do_login(self.user), "login failed")
        self.client.post(self.delete_url)
        self.assertEqual(len(Caffeine.objects.filter(user=self.user)), 0)

    def test_cannot_delete_other_users_caffeine(self):
        self.assertTrue(self._do_login(self.user), "login failed")
        mateguy = User.objects.create_user(
            username="mateguy", email="mrmate@example.org"
        )
        othercaffeine = Caffeine.objects.create(
            user=mateguy, ctype=DRINK_TYPES.mate, date=timezone.now()
        )
        self.assertEqual(len(Caffeine.objects.filter(user=mateguy)), 1)
        response = self.client.post("/delete/{}/".format(othercaffeine.id))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(len(Caffeine.objects.filter(user=mateguy)), 1)

    def test_success_message(self):
        self.assertTrue(self._do_login(self.user), "login failed")
        response = self.client.post(self.delete_url, follow=True)
        self.assertMessageCount(response, 1)
        self.assertMessageContains(
            response, DELETE_CAFFEINE_SUCCESS_MESSAGE, messages.SUCCESS
        )


class SelectTimeZoneViewTest(MessagesTestMixin, CaffeineViewTest):
    def setUp(self):
        super(SelectTimeZoneViewTest, self).setUp()
        self.url = "/selecttimezone/"
        self.user = self._create_testuser()

    def test_redirects_to_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, "/auth/login/?next={}".format(self.url))

    def test_redirects_to_profile(self):
        self.assertTrue(self._do_login(self.user), "login failed")
        response = self.client.post(self.url, data={"timezone": "Europe/Berlin"})
        self.assertRedirects(response, "/profile/")

    def test_redirects_to_next(self):
        self.assertTrue(self._do_login(self.user), "login failed")
        response = self.client.post(
            "{}?next=/settings/".format(self.url), data={"timezone": "Europe/Berlin"}
        )
        self.assertRedirects(response, "/settings/")

    def test_avoids_redirect_loop(self):
        self.assertTrue(self._do_login(self.user), "login failed")
        response = self.client.post(
            "{}?next={}".format(self.url, self.url), data={"timezone": "Europe/Berlin"}
        )
        self.assertRedirects(response, "/profile/")

    def test_no_timezone_error(self):
        self.assertTrue(self._do_login(self.user), "login failed")
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertIn("timezone", response.context["form"].errors)
        self.assertEqual(
            response.context["form"].errors["timezone"][0], EMPTY_TIMEZONE_ERROR
        )

    def test_tzlist_in_context(self):
        self.assertTrue(self._do_login(self.user), "login failed")
        response = self.client.get(self.url)
        self.assertIn("tzlist", response.context)

    def test_render_selecttimezone_template(self):
        self.assertTrue(self._do_login(self.user), "login failed")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "selecttimezone.html")

    def test_render_timezone_changed(self):
        self.assertTrue(self._do_login(self.user), "login failed")
        self.client.post(self.url, data={"timezone": "Europe/London"})
        self.assertEqual(
            User.objects.get(username=self.user.username).timezone, "Europe/London"
        )

    def test_success_message(self):
        self.assertTrue(self._do_login(self.user), "login failed")
        response = self.client.post(
            self.url, data={"timezone": "Europe/London"}, follow=True
        )
        self.assertMessageCount(response, 1)
        self.assertMessageContains(
            response, SELECT_TIMEZONE_SUCCESS_MESSAGE % {"timezone": "Europe/London"}
        )


class RandomUsersTest(TestCase):
    def setUp(self):
        super(RandomUsersTest, self).setUp()
        self.user = User.objects.create_user(
            "testuser",
            "test@example.org",
            password=_TEST_PASSWORD,
            token="testtoken",
            is_active=True,
        )
        self.user.timezone = "Europe/Berlin"
        self.user.save()

    def _do_login(self):
        self.assertTrue(
            self.client.login(username=self.user.username, password=_TEST_PASSWORD),
            "login failed",
        )

    def test_requires_login(self):
        myurl = reverse("random_users")
        response = self.client.get(myurl)
        self.assertRedirects(
            response, "{}?next={}".format(reverse("auth_login"), myurl)
        )

    def test_missing_count_yields_fife_users(self):
        for num in range(10):
            User.objects.create_user(
                "test{}".format(num + 1),
                "test{}@example.org".format(num + 1),
                token="testtoken{}".format(num + 1),
                date_joined=timezone.now() - timedelta(days=num),
            )
        self._do_login()

        response = self.client.get(reverse("random_users"))
        self.assertEqual(response["content-type"], "text/json")
        data = json.loads(response.content)
        self.assertEqual(len(data), 5)

    def test_get_random_users(self):
        for num in range(10):
            User.objects.create_user(
                "test{}".format(num + 1),
                "test{}@example.org".format(num + 1),
                token="testtoken{}".format(num + 1),
                date_joined=timezone.now() - timedelta(days=num),
            )
        self._do_login()

        response = self.client.get("{}?count=4".format(reverse("random_users")))
        self.assertEqual(response["content-type"], "text/json")
        data = json.loads(response.content)
        self.assertEqual(len(data), 4)
        for item in data:
            self.assertTrue(item["username"].startswith("test"))
            for key in ("username", "name", "location", "profile", "coffees", "mate"):
                self.assertIn(key, item)
