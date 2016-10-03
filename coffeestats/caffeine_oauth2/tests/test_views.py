from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.test import TransactionTestCase

from caffeine_oauth2.models import CoffeestatsApplication
from caffeine_oauth2.views import CoffeestatsApplicationRegistration

User = get_user_model()


class CoffeestatsApplicationRegistrationTest(TransactionTestCase):
    def test_get_form_class(self):
        view = CoffeestatsApplicationRegistration()
        form_class = view.get_form_class()
        self.assertIsNotNone(form_class)
        self.assertEqual(form_class.Meta.model, CoffeestatsApplication)

    def setUp(self):
        self.user = User.objects.create(
            username='tester', timezone='Europe/Berlin')
        self.post_data = {
            'agree': False, 'website': 'http://foo.example.org/',
            'client_type': CoffeestatsApplication.CLIENT_PUBLIC,
            'name': 'The foo coffeestats API client',
            'description': 'A foo client from the knights of foo',
            'client_id': 'test_id',
            'authorization_grant_type': CoffeestatsApplication.GRANT_IMPLICIT,
            'redirect_uris': 'http://localhost:8001/',
        }
        self.client.force_login(self.user)

    def test_register_application_template(self):
        response = self.client.get(reverse('oauth2_provider:register'))
        self.assertTemplateUsed(
            response, 'oauth2_provider/application_registration_form.html')

    def test_valid_application_redirect(self):
        response = self.client.post(
            reverse('oauth2_provider:register'), data=self.post_data)
        # check that the response is a redirect to the pending application
        # page
        self.assertIsNotNone(response)
        self.assertIn('application', response.context)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, reverse(
            'oauth2_provider:detail',
            kwargs={'pk': response.context['application'].id}))

    def test_valid_application_use_pending_template(self):
        response = self.client.post(
            reverse('oauth2_provider:register'), data=self.post_data,
            follow=True)
        self.assertIsNotNone(response)
        self.assertTemplateUsed('caffeine_oauth2/pending_approval.html')

    def test_valid_application_email_to_staff(self):
        response = self.client.post(
            reverse('oauth2_provider:register'), data=self.post_data)
        self.assertEqual(len(mail.outbox), 1)
        mail_item = mail.outbox[0]
        current_site = get_current_site(response.request)
        application = response.context['application']
        approval_url = reverse('oauth2_provider:approve',
                               kwargs={'pk': application.id})
        self.assertEqual(
            mail_item.subject,
            '[{}] A new API client {} has been requested'.format(
                current_site.name, application.name
            ))
        self.assertEqual(len(mail_item.alternatives), 1)
        self.assertEqual(mail_item.alternatives[0][1], 'text/html')
        text_content = str(mail_item.body)
        html_content = str(mail_item.alternatives[0][0])
        for content in (application.name, application.description,
                        str(self.user), application.website, approval_url):
            self.assertIn(content, text_content)
            self.assertIn(content, html_content)
        self.assertEqual(mail_item.from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(len(mail_item.to), len(settings.ADMINS))
        for recipient in [admin[1] for admin in settings.ADMINS]:
            self.assertIn(recipient, mail_item.to)


class CoffeestatsApplicationApprovalTest(TransactionTestCase):
    def setUp(self):
        self.appuser = User.objects.create(
            username='appuser', email='appuser@example.org')
        self.application = CoffeestatsApplication.objects.create(
            user=self.appuser, agree=False, website='http://foo.example.org/',
            client_type=CoffeestatsApplication.CLIENT_PUBLIC,
            name='The foo coffeestats API client',
            description='A foo client from the knights of foo',
            authorization_grant_type=CoffeestatsApplication.GRANT_IMPLICIT,
            redirect_uris='http://localhost:8001/'
        )
        self.post_data = {
            'name': 'The foo API client',
            'description': 'Third party foo client from the knights of foo',
            'website': self.application.website,
            'client_type': self.application.client_type,
            'authorization_grant_type': CoffeestatsApplication.GRANT_IMPLICIT,
        }
        self.user = User.objects.create_superuser(
            username='admin', email='coffeestats@example.org',
            password='s3cr3t', timezone='Europe/Berlin')
        self.client.force_login(self.user)

    def test_approve_application_template(self):
        response = self.client.get(reverse(
            'oauth2_provider:approve', kwargs={'pk': self.application.id}))
        self.assertTemplateUsed(response, 'caffeine_oauth2/approve.html')

    def test_valid_approval_redirect(self):
        response = self.client.post(reverse(
            'oauth2_provider:approve', kwargs={'pk': self.application.id}),
            data=self.post_data)
        # check that the response is a redirect to the application list page
        self.assertIsNotNone(response)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, reverse('oauth2_provider:list_all'))

    def test_valid_approval_email_to_applicant(self):
        response = self.client.post(reverse(
            'oauth2_provider:approve', kwargs={'pk': self.application.id}),
            data=self.post_data)
        self.assertEqual(len(mail.outbox), 1)
        mail_item = mail.outbox[0]
        current_site = get_current_site(response.request)
        detail_url = reverse('oauth2_provider:detail',
                             kwargs={'pk': self.application.id})
        self.assertEqual(
            mail_item.subject,
            '[{}] Your API client {} has been approved'.format(
                current_site.name, self.post_data['name'],
            )
        )
        self.assertEqual(len(mail_item.alternatives), 1)
        self.assertEqual(mail_item.alternatives[0][1], 'text/html')
        text_content = str(mail_item.body)
        html_content = str(mail_item.alternatives[0][0])
        for content in (detail_url, self.post_data['name']):
            self.assertIn(content, text_content)
            self.assertIn(content, html_content)
        self.assertEqual(mail_item.from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(len(mail_item.to), 1)
        self.assertIn(self.appuser.email, mail_item.to)


class CoffeestatsApplicationRejectionTest(TransactionTestCase):
    def setUp(self):
        self.appuser = User.objects.create(
            username='appuser', email='appuser@example.org')
        self.application = CoffeestatsApplication.objects.create(
            user=self.appuser, agree=False, website='http://foo.example.org/',
            client_type=CoffeestatsApplication.CLIENT_PUBLIC,
            name='The foo coffeestats API client',
            description='A foo client from the knights of foo',
            authorization_grant_type=CoffeestatsApplication.GRANT_IMPLICIT,
            redirect_uris='http://localhost:8001/'
        )
        self.post_data = {
            'reasoning': 'It sucks! Really this is not a good idea.',
        }
        self.user = User.objects.create_superuser(
            username='admin', email='coffeestats@example.org',
            password='s3cr3t', timezone='Europe/Berlin')
        self.client.force_login(self.user)

    def test_approve_application_template(self):
        response = self.client.get(reverse(
            'oauth2_provider:reject', kwargs={'pk': self.application.id}))
        self.assertTemplateUsed(response, 'caffeine_oauth2/reject.html')

    def test_valid_reject_redirect(self):
        response = self.client.post(reverse(
            'oauth2_provider:reject', kwargs={'pk': self.application.id}),
            data=self.post_data)
        self.assertIsNotNone(response)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, reverse('oauth2_provider:list_all'))

    def test_valid_reject_email_to_applicant(self):
        response = self.client.post(reverse(
            'oauth2_provider:reject', kwargs={'pk': self.application.id}),
            data=self.post_data)
        with self.assertRaises(CoffeestatsApplication.DoesNotExist):
            CoffeestatsApplication.objects.get(pk=self.application.id)
        self.assertEqual(len(mail.outbox), 1)
        mail_item = mail.outbox[0]
        current_site = get_current_site(response.request)
        self.assertEqual(
            mail_item.subject,
            '[{}] Your API client {} has been rejected'.format(
                current_site.name, self.application.name))
        self.assertEqual(len(mail_item.alternatives), 1)
        self.assertEqual(mail_item.alternatives[0][1], 'text/html')
        text_content = str(mail_item.body)
        html_content = str(mail_item.alternatives[0][0])
        for content in (self.application.name, self.post_data['reasoning']):
            self.assertIn(content, text_content)
            self.assertIn(content, html_content)
        self.assertEqual(mail_item.from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(len(mail_item.to), 1)
        self.assertIn(self.appuser.email, mail_item.to)
