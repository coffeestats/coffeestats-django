import re

from django.test import LiveServerTestCase
from django.core import mail

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from six.moves.urllib import parse


simple_url_re = re.compile(
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|'
    '(?:%[0-9a-fA-F][0-9a-fA-F]))+',
    re.IGNORECASE | re.MULTILINE)


class SeleniumTest(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.selenium = webdriver.Firefox()
        cls.selenium.implicitly_wait(10)
        super(SeleniumTest, cls).setUpClass()
        cls.server_url = cls.live_server_url

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(SeleniumTest, cls).tearDownClass()


class BaseCoffeeStatsPageTestMixin(object):
    TEST_USERNAME = 'coffeejunkie'
    TEST_PASSWORD = 'g3h31m!1elf!!'
    TEST_EMAILADDRESS = 'coffeejunkie@example.org'

    def check_page_header(self):
        # The caffeine junkie sees that the page title mention coffeestats and
        # looks at the awesome headline and slogan in the header
        self.assertIn('coffeestats', self.selenium.title)
        header = self.selenium.find_element_by_id('header')
        # the title links to the home page
        homelink = header.find_element_by_link_text('coffeestats.org')
        self.assertEqual(homelink.get_attribute('href'),
                         '{}/'.format(self.server_url))

        # the title has the awesome slogan title
        self.assertEqual(homelink.get_attribute('title'),
                         '... about what keeps you awake at night')

    def check_page_footer(self):
        # the footer contains links to the home page, the authors' web sites
        # and the imprint
        footer = self.selenium.find_element_by_class_name('footer')

        expected_footer_links = [
            (u'coffeestats.org', u'{}/'.format(self.server_url)),
            (u'Jan Dittberner', u'https://jan.dittberner.info/'),
            (u'Jeremias Arnstadt', u'http://www.art-ifact.de/'),
            (u'Florian Baumann', u'http://noqqe.de/'),
            (u'Imprint', u'{}/imprint/'.format(self.server_url))
        ]

        self.assertEqual(
            [(link.text, link.get_attribute('href')) for link in
             footer.find_elements_by_tag_name('a')],
            expected_footer_links)

    def navigate_to_register_page(self):
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

    def extract_link(self, data):
        match = simple_url_re.search(data)
        if not match:
            self.fail('no link found')
        urlparts = list(parse.urlsplit(match.group(0)))
        urlparts[:2] = ['', '']
        urlremainder = parse.urlunsplit(urlparts)
        return parse.urljoin(self.server_url, urlremainder)

    def register_user(self):
        self.navigate_to_register_page()

        input_username = self.selenium.switch_to.active_element
        input_username.send_keys(self.TEST_USERNAME + Keys.TAB)

        input_password1 = self.selenium.switch_to.active_element
        input_password1.send_keys(self.TEST_PASSWORD + Keys.TAB)

        input_password2 = self.selenium.switch_to.active_element
        input_password2.send_keys(self.TEST_PASSWORD + Keys.TAB)

        input_email = self.selenium.switch_to.active_element
        input_email.send_keys(self.TEST_EMAILADDRESS)

        input_email.submit()

        self.assertEqual(len(mail.outbox), 1)
        activation_link = self.extract_link(mail.outbox[0].body)

        self.selenium.get(activation_link)

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

        tzselect = self.selenium.find_element_by_id('tzselect')
        action_chain = ActionChains(self.selenium)
        action_chain.move_to_element(tzselect).perform()

        tzselect.submit()
        mail.outbox = []
