from django.test import LiveServerTestCase
from selenium import webdriver


class SeleniumTest(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.selenium = webdriver.Firefox()
        cls.selenium.implicitly_wait(3)
        super(SeleniumTest, cls).setUpClass()
        cls.server_url = cls.live_server_url

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()


class BaseCoffeeStatsPageTestMixin(object):

    def check_page_header(self):
        # The caffeine junkie sees that the page title mention coffeestats and
        # looks at the awesome headline and slogan in the header
        self.assertIn('coffeestats', self.selenium.title)
        header = self.selenium.find_element_by_id('header')
        # the title links to the home page
        homelink = header.find_element_by_link_text('coffeestats.org')
        self.assertEqual(homelink.get_attribute('href'),
                         '{}/'.format(self.server_url))

        # the header contains the awesome slogan
        self.assertIn('... about what keeps you awake at night', header.text)

    def check_page_footer(self):
        # the footer contains links to the home page, the authors' web sites
        # and the imprint
        footer = self.selenium.find_element_by_class_name('footer')

        expected_footer_links = [
            (u'coffeestats.org', u'{}/'.format(self.server_url)),
            (u'Jan Dittberner', u'https://jan.dittberner.info/'),
            (u'Florian Baumann', u'http://noqqe.de/'),
            (u'Imprint', u'{}/imprint/'.format(self.server_url))
        ]

        self.assertEqual(
            [(link.text, link.get_attribute('href')) for link in
             footer.find_elements_by_tag_name('a')],
            expected_footer_links)
