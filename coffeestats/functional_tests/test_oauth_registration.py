from __future__ import unicode_literals

import re
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.urlresolvers import reverse
from django.utils.http import urlquote
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

from .base import BaseCoffeeStatsPageTestMixin, SeleniumTest

ADMIN_EMAIL = 'admin@example.org'
ADMIN_PASSWORD = 'm0r3s3cr#t'
ADMIN_USERNAME = 'admin'
APPLICANT_EMAIL = 'test@example.org'
APPLICANT_PASSWORD = 's3cr3t'
APPLICANT_USERNAME = 'testuser'
DEFAULT_TIMEZONE = 'Europe/Berlin'

User = get_user_model()


class RegisterApplicationTest(BaseCoffeeStatsPageTestMixin, SeleniumTest):
    def setUp(self):
        # prepare a regular and a staff user
        self.applicant = User.objects.create_user(
            username=APPLICANT_USERNAME, email=APPLICANT_EMAIL,
            password=APPLICANT_PASSWORD, timezone=DEFAULT_TIMEZONE)
        self.admin = User.objects.create_superuser(
            username=ADMIN_USERNAME, email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD, timezone=DEFAULT_TIMEZONE)

    def goto_application_registration(self):
        # user visits the start page and logs in
        self.selenium.get(self.server_url)
        header = self.selenium.find_element_by_id('header')
        nav = header.find_element_by_tag_name('nav')
        login_subnav = nav.find_element_by_tag_name('span')
        action_chain = ActionChains(self.selenium)
        action_chain.move_to_element(login_subnav).perform()

        username_field = self.selenium.find_element_by_id('id_login_username')
        username_field.send_keys(APPLICANT_USERNAME + Keys.TAB)
        password_field = self.selenium.switch_to.active_element
        self.assertEqual(
            password_field.get_attribute('id'), 'id_login_password')
        password_field.send_keys(APPLICANT_PASSWORD + Keys.ENTER)

        # user is redirected to the profile page
        self.assertRegexpMatches(self.selenium.current_url, r'/profile/$')

        # user looks for the settings link in the navigation and clicks it
        header = self.selenium.find_element_by_id('header')
        nav = header.find_element_by_tag_name('nav')
        settings_menu = nav.find_element_by_class_name('settings')
        action_chain = ActionChains(self.selenium)
        action_chain.move_to_element(settings_menu).perform()
        settings_link = nav.find_element_by_link_text('Settings')
        settings_link.click()

        # user is redirected to the profile page
        self.assertRegexpMatches(self.selenium.current_url, r'/settings/$')

        # find application registration link and click it
        reglink = self.selenium.find_element_by_link_text(
            'Register a new application')
        reglink.click()

        # user sees a form
        regform = self.selenium.find_element_by_tag_name('form')
        self.assertTrue(
            self.selenium.current_url.endswith(regform.get_attribute('action'))
        )

    def test_register_oauth2_client(self):
        self.goto_application_registration()

        # enter application name
        name_field = self.selenium.find_element_by_id('id_name')
        name_field.send_keys('Little test application' + Keys.TAB)

        description_field = self.selenium.switch_to.active_element
        self.assertEqual(
            description_field.get_attribute('id'), 'id_description')
        description_field.send_keys(
            'Little do we know about the usage of coffee, this application '
            'will bring global transparency for coffee world domination.' +
            Keys.TAB)

        website_field = self.selenium.switch_to.active_element
        self.assertEqual(website_field.get_attribute('id'), 'id_website')
        website_field.send_keys(
            'https://coffeeapp.example.org/' + Keys.TAB)

        agree_field = self.selenium.switch_to.active_element
        self.assertEqual(agree_field.get_attribute('id'), 'id_agree')
        action_chain = ActionChains(self.selenium)
        action_chain.click(agree_field).perform()
        agree_field.send_keys(Keys.TAB)

        client_type_field = self.selenium.switch_to.active_element
        self.assertEqual(
            client_type_field.get_attribute('id'), 'id_client_type')
        self.assertEqual(client_type_field.tag_name, 'select')
        choice = Select(client_type_field)
        choice.select_by_visible_text('Public')
        client_type_field.send_keys(Keys.TAB)

        authorization_grant_type_field = self.selenium.switch_to.active_element
        self.assertEqual(
            authorization_grant_type_field.get_attribute('id'),
            'id_authorization_grant_type')
        self.assertEqual(client_type_field.tag_name, 'select')
        choice = Select(authorization_grant_type_field)
        choice.select_by_visible_text('Implicit')
        authorization_grant_type_field.send_keys(Keys.TAB)

        redirect_uris_field = self.selenium.switch_to.active_element
        self.assertEqual(
            redirect_uris_field.get_attribute('id'), 'id_redirect_uris')
        redirect_uris_field.send_keys(
            'https://coffeeapp.example.org/auth/' + Keys.ENTER +
            'org.coffeestats.cli://auth/' + Keys.TAB)

        go_back_button = self.selenium.switch_to.active_element
        self.assertEqual(go_back_button.text, 'Go Back')
        self.assertRegexpMatches(
            go_back_button.get_attribute('href'), r'/oauth2/applications/$')
        go_back_button.send_keys(Keys.TAB)

        submit_button = self.selenium.switch_to.active_element
        self.assertEqual(submit_button.tag_name, 'button')
        self.assertEqual(submit_button.get_attribute('type'), 'submit')
        submit_button.click()

        # the application registration is submitted and the user lands on the
        # pending application page
        self.assertRegexpMatches(
            self.selenium.current_url, r'/oauth2/applications/\d+/pending/$')
        application_id = re.search(
            r'(?<=/oauth2/applications/)\d+',
            self.selenium.current_url).group(0)

        # TODO: check that client_id and client_secret are not shown

        # user performs a logout
        header = self.selenium.find_element_by_id('header')
        nav = header.find_element_by_tag_name('nav')
        settings_menu = nav.find_element_by_class_name('settings')
        action_chain = ActionChains(self.selenium)
        action_chain.move_to_element(settings_menu).perform()
        self.selenium.find_element_by_link_text('Logout').click()

        # a mail with an approval link has been sent to the admins
        self.assertEqual(len(mail.outbox), 1)
        registered_mail = mail.outbox[0]
        self.assertEqual(len(registered_mail.to), len(settings.ADMINS))
        for admin in settings.ADMINS:
            self.assertIn(admin[1], registered_mail.to)
        approval_url = reverse(
            'oauth2_provider:approve', kwargs={'pk': application_id})
        self.assertIn(approval_url, registered_mail.body)

        # the admin user opens the approval link and sees a login page
        self.selenium.get(self.server_url + approval_url)
        self.assertRegexpMatches(
            self.selenium.current_url, r'/login/\?next=')
        self.assertTrue(
            self.selenium.current_url.endswith(urlquote(approval_url)))

        username_field = self.selenium.find_element_by_id('id_login_username')
        username_field.send_keys(ADMIN_USERNAME + Keys.TAB)
        password_field = self.selenium.switch_to.active_element
        self.assertEqual(
            password_field.get_attribute('id'), 'id_login_password')
        password_field.send_keys(ADMIN_PASSWORD + Keys.ENTER)

        # the admin user is now redirected to the approval page
        self.assertTrue(self.selenium.current_url.endswith(approval_url))

        approve_button = self.selenium.find_element_by_tag_name('button')
        self.assertEqual(approve_button.tag_name, 'button')
        self.assertEqual(approve_button.get_attribute('type'), 'submit')
        self.assertEqual(approve_button.text, 'Approve')
        approve_button.click()

        self.assertRegexpMatches(
            self.selenium.current_url, r'/oauth2/all-applications/$')

        # TODO: check that a link to the application page exists

        # a mail with the approval success and an application detail page link
        # has been sent to the applicant
        self.assertEqual(len(mail.outbox), 2)
        approval_mail = mail.outbox[1]
        self.assertEqual(len(approval_mail.to), 1)
        self.assertIn(APPLICANT_EMAIL, approval_mail.to)
        application_detail_url = reverse(
            'oauth2_provider:detail', kwargs={'pk': application_id})
        self.assertIn(application_detail_url, approval_mail.body)

        # TODO: check that client_id and client_secret are shown in detail page
