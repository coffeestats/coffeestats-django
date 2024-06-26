import re
import sys
from datetime import datetime

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import mail
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from six.moves.urllib import parse

simple_url_re = re.compile(
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
    re.IGNORECASE | re.MULTILINE,
)


class SeleniumTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        options = ChromeOptions()
        options.headless = True
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--privileged")
        options.add_argument("--window-size=1920,1080")
        cls.selenium = webdriver.Chrome()
        cls.selenium.implicitly_wait(10)
        super(SeleniumTest, cls).setUpClass()
        cls.server_url = cls.live_server_url

    def tearDown(self):
        if sys.exc_info()[0]:
            test_method_name = self._testMethodName
            self.selenium.get_screenshot_as_file(
                "screenshot-{0}-{1}.png".format(
                    datetime.now().strftime("%Y%m%d-%H%M%S"), test_method_name
                )
            )

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(SeleniumTest, cls).tearDownClass()


class BaseCoffeeStatsPageTestMixin(object):
    TEST_USERNAME = "coffeejunkie"
    TEST_PASSWORD = "g3h31m!1elf!!"
    TEST_EMAILADDRESS = "coffeejunkie@example.org"

    def check_page_header(self):
        # The caffeine junkie sees that the page title mention coffeestats and
        # looks at the awesome headline and slogan in the header
        self.assertIn("coffeestats", self.selenium.title)

        # find favicon and touch icons
        favicons = self.selenium.find_elements(
            by=By.CSS_SELECTOR, value='link[rel="shortcut icon"]'
        )
        self.assertEqual(len(favicons), 1)

        touchicons = self.selenium.find_elements(
            by=By.CSS_SELECTOR, value='link[rel="apple-touch-icon"]'
        )
        self.assertEqual(len(touchicons), 4)
        sizes = (None, "72x72", "114x114", "144x144")
        for icidx in range(4):
            self.assertEqual(touchicons[icidx].get_attribute("sizes"), sizes[icidx])

        header = self.selenium.find_element(by=By.ID, value="header")
        # the title links to the home page
        homelink = header.find_element(by=By.LINK_TEXT, value="coffeestats.org")
        self.assertEqual(homelink.get_attribute("href"), "{}/".format(self.server_url))

        # the title has the awesome slogan title
        self.assertEqual(
            homelink.get_attribute("title"), "... about what keeps you awake at night"
        )

    def check_page_footer(self):
        # the footer contains links to the home page, the authors' web sites
        # and the imprint
        footer = self.selenium.find_element(by=By.CLASS_NAME, value="footer")

        expected_footer_links = [
            ("coffeestats.org", "{}/".format(self.server_url)),
            ("Jan Dittberner", "https://jan.dittberner.info/"),
            ("Jeremias Arnstadt", "http://www.art-ifact.de/"),
            ("Florian Baumann", "http://noqqe.de/"),
            ("Imprint", "{}/imprint/".format(self.server_url)),
        ]

        self.assertEqual(
            [
                (link.text, link.get_attribute("href"))
                for link in footer.find_elements(by=By.TAG_NAME, value="a")
            ],
            expected_footer_links,
        )

    def navigate_to_register_page(self):
        # Coffeejunkie has opens the homepage
        self.selenium.get(self.server_url)

        self.check_page_header()

        # He finds out that he was redirected to the home page
        self.assertRegex(self.selenium.current_url, r"/$")

        # there is a navigation in the page header
        header = self.selenium.find_element(by=By.ID, value="header")
        nav = header.find_element(by=By.TAG_NAME, value="nav")

        # He wants to register and finds the register_link
        register_link = nav.find_element(by=By.LINK_TEXT, value="Register")
        register_link.click()

        # He finds out that he is now on the django_registration page
        self.assertRegex(self.selenium.current_url, r"/auth/register/$")

    def extract_link(self, data):
        match = simple_url_re.search(data)
        if not match:
            self.fail("no link found")
        urlparts = list(parse.urlsplit(match.group(0)))
        urlparts[:2] = ["", ""]
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

        header = self.selenium.find_element(by=By.ID, value="header")
        nav = header.find_element(by=By.TAG_NAME, value="nav")
        login_subnav = nav.find_element(by=By.TAG_NAME, value="span")
        action_chain = ActionChains(self.selenium)
        action_chain.move_to_element(login_subnav).perform()

        username_field = self.selenium.find_element(by=By.ID, value="id_login_username")
        username_field.send_keys(self.TEST_USERNAME + Keys.TAB)

        password_field = self.selenium.switch_to.active_element
        self.assertEqual(password_field.get_attribute("id"), "id_login_password")
        password_field.send_keys(self.TEST_PASSWORD + Keys.ENTER)

        tzselect = self.selenium.find_element(by=By.ID, value="tzselect")
        action_chain = ActionChains(self.selenium)
        action_chain.move_to_element(tzselect).perform()

        # submits the form
        submit_button = self.selenium.find_element(by=By.ID, value="submit")
        submit_button.click()

        mail.outbox = []
