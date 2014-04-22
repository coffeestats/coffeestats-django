from django.core import mail
from django.test import TestCase
from django.contrib import messages
from django.contrib.auth import get_user_model

from caffeine.views import (
    DELETE_ACCOUNT_MESSAGE,
    EXPORT_SUCCESS_MESSAGE,
)


User = get_user_model()


class CaffeineViewTest(TestCase):

    def _do_login(self):
        user = User.objects.create_user(
            username='testuser', email='test@bla.com',
            password='test1234')
        user.timezone = 'Europe/Berlin'
        user.save()
        return self.client.login(username='testuser', password='test1234')


class MessagesTestMixin(object):

    def assertMessageCount(self, response, expected_num):
        self.assertEqual(len(response.context['messages']),
                         expected_num)

    def assertMessageContains(self, response, text, level=None):
        response_messages = response.context['messages']
        matches = [m for m in response_messages if text in m.message]

        if len(matches) == 1:
            msg = matches[0]
            if level is not None and msg.level != level:
                self.fail('There was one matching message but different'
                          ' level: %s != %s' % (msg.level, level))
        elif len(matches) == 0:
            messages_str = ', '.join('"%s"' % m for m in response_messages)
            self.fail('No message contained text "%s", messages were: %s' %
                      (text, messages_str))
        else:
            self.fail('Multiple messages contained text "%s": %s' %
                      (text, ', '.join(('"%s"' % m) for m in matches)))


class AboutViewTest(CaffeineViewTest):

    def test_redirects_to_login(self):
        response = self.client.get('/about/')
        self.assertRedirects(
            response, '/auth/login/?next=/about/')

    def test_renders_about_template(self):
        self.assertTrue(self._do_login(), 'login failed')
        response = self.client.get('/about/')
        self.assertTemplateUsed(response, 'about.html')


class ExploreViewTest(CaffeineViewTest):

    def test_redirects_to_login(self):
        response = self.client.get('/explore/')
        self.assertRedirects(
            response, '/auth/login/?next=/explore/')

    def test_renders_explore_template(self):
        self.assertTrue(self._do_login(), 'login failed')
        response = self.client.get('/explore/')
        self.assertTemplateUsed(response, 'explore.html')

    def test_context_items(self):
        self.assertTrue(self._do_login(), 'login failed')
        response = self.client.get('/explore/')
        for item in ('activities', 'users', 'topcoffee',
                     'topcoffeeavg', 'topmate', 'topmateavg',
                     'recentlyjoined', 'longestjoined'):
            self.assertIn(item, response.context)


class ExportActivityView(MessagesTestMixin, CaffeineViewTest):

    def test_redirects_to_login(self):
        response = self.client.get('/activity/export/')
        self.assertRedirects(
            response, '/auth/login/?next=/activity/export/')

    def test_sends_csv_mail(self):
        self.assertTrue(self._do_login(), 'login failed')
        response = self.client.get('/activity/export/', follow=True)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Your caffeine records')
        self.assertMessageCount(response, 1)
        self.assertMessageContains(
            response, EXPORT_SUCCESS_MESSAGE, messages.INFO)


class DeleteAccountViewTest(MessagesTestMixin, CaffeineViewTest):

    def test_redirects_to_login(self):
        response = self.client.get('/deletemyaccount/')
        self.assertRedirects(
            response, '/auth/login/?next=/deletemyaccount/')

    def test_renders_delete_confirmation_template(self):
        self.assertTrue(self._do_login(), 'login failed')
        response = self.client.get('/deletemyaccount/')
        self.assertTemplateUsed(response, 'caffeine/user_confirm_delete.html')
        self.assertIn('user', response.context)

    def test_delete(self):
        self.assertTrue(self._do_login(), 'login failed')
        response = self.client.post('/deletemyaccount/', follow=True)
        self.assertMessageCount(response, 1)
        self.assertMessageContains(
            response, DELETE_ACCOUNT_MESSAGE, messages.INFO)
        self.assertFalse(self.client.login(
            username='testuser', password='test1234'))
