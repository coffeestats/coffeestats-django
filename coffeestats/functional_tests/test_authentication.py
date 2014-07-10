import re

from django.core import mail
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from six.moves.urllib import parse

from .base import BaseCoffeeStatsPageTestMixin, SeleniumTest


simple_url_re = re.compile(
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|'
    '(?:%[0-9a-fA-F][0-9a-fA-F]))+',
    re.IGNORECASE | re.MULTILINE)


class RegisterUserTest(BaseCoffeeStatsPageTestMixin, SeleniumTest):
    TEST_USERNAME = 'coffeejunkie'
    TEST_PASSWORD = 'g3h31m!1elf!!'
    TEST_EMAILADDRESS = 'coffeejunkie@example.org'

    def test_register_user(self):
        # Coffeejunkie has opens the homepage
        self.selenium.get(self.server_url)

        self.check_page_header()

        # He finds out that he was redirected to a login page
        self.assertRegexpMatches(self.selenium.current_url,
                                 r'/auth/login/\?next=/$')

        # there is a navigation in the page header
        header = self.selenium.find_element_by_id('header')
        nav = header.find_element_by_tag_name('nav')

        # He wants to register and finds the register_link
        register_link = nav.find_element_by_link_text('Register')
        register_link.click()

        # He finds out that he is now on the registration page
        self.assertRegexpMatches(self.selenium.current_url,
                                 r'/auth/register/$')

        # he finds the input fields and enters ...
        # ... his desired user name
        input_username = self.selenium.switch_to.active_element
        self.assertEqual(input_username.get_attribute('id'), 'id_username')
        input_username.send_keys(self.TEST_USERNAME + Keys.TAB)

        input_password1 = self.selenium.switch_to.active_element
        self.assertEqual(input_password1.get_attribute('id'), 'id_password1')
        input_password1.send_keys(self.TEST_PASSWORD)

        # he hits enter and gets a validation error
        input_password1.submit()

        input_password1 = self.selenium.find_element_by_id('id_password1')

        elems = input_password1.parent.find_elements_by_css_selector(
            'ul.errorlist')
        self.assertEqual(len(elems), 2)  # one error for email one for password

        # the cursor is on the username input field
        input_username = self.selenium.switch_to.active_element
        self.assertEqual(input_username.get_attribute('id'), 'id_username')
        self.assertEqual(input_username.get_attribute('value'),
                         self.TEST_USERNAME)

        # he continues his registration
        input_username.send_keys(Keys.TAB)

        input_password1 = self.selenium.switch_to.active_element
        self.assertEqual(input_password1.get_attribute('id'), 'id_password1')
        input_password1.send_keys(self.TEST_PASSWORD + Keys.TAB)

        input_password2 = self.selenium.switch_to.active_element
        self.assertEqual(input_password2.get_attribute('id'), 'id_password2')
        input_password2.send_keys(self.TEST_PASSWORD + Keys.TAB)

        input_email = self.selenium.switch_to.active_element
        self.assertEqual(input_email.get_attribute('id'), 'id_email')
        input_email.send_keys(self.TEST_EMAILADDRESS)

        # he submits the form
        input_email.submit()

        # ... and is redirected to the landing page
        self.assertRegexpMatches(self.selenium.current_url,
                                 r'/auth/login/\?next=/$')

        # ... and gets an email with an activation link
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Please activate your account', mail.outbox[0].subject)
        self.assertIn(self.TEST_EMAILADDRESS, mail.outbox[0].to)

        match = simple_url_re.search(mail.outbox[0].body, re.MULTILINE)
        if not match:
            self.fail('no activation link found')
        urlparts = list(parse.urlsplit(match.group(0)))
        urlparts[:2] = ['', '']
        urlremainder = parse.urlunsplit(urlparts)
        activation_link = parse.urljoin(self.server_url, urlremainder)

        # he opens the activation link
        self.selenium.get(activation_link)

        content = self.selenium.find_element_by_css_selector('body')
        self.assertIn(
            'Your account has been activated successfully.',
            content.text
        )

        # he opens the login form and enters his credentials
        header = self.selenium.find_element_by_id('header')
        nav = header.find_element_by_tag_name('nav')
        login_subnav = nav.find_element_by_tag_name('span')
        action_chain = ActionChains(self.selenium)
        action_chain.move_to_element(login_subnav).perform()

        username_field = self.selenium.find_element_by_id('id_login_username')
        username_field.send_keys(self.TEST_USERNAME + Keys.TAB)

        password_field = self.selenium.switch_to.active_element
        self.assertEqual(password_field.get_attribute('id'),
                         'id_login_password')
        password_field.send_keys(self.TEST_PASSWORD + Keys.ENTER)

        # ... and is redirected to the timezone selection page
        self.assertRegexpMatches(self.selenium.current_url,
                                 r'/selecttimezone/\?next=%2Fprofile%2F$')
