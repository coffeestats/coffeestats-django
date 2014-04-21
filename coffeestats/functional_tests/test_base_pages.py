from .base import BaseCoffeeStatsPageTestMixin, SeleniumTest


class BasicPageTest(BaseCoffeeStatsPageTestMixin, SeleniumTest):

    def test_check_homepage_elements(self):
        # Coffeejunkie has heard about coffeestats and wants to visit the
        # homepage
        self.selenium.get(self.server_url)

        self.check_page_header()

        # He finds out that he was redirected to a login page
        self.assertRegexpMatches(self.selenium.current_url,
                                 r'/auth/login/\?next=/$')

        # He sees 3 boxes
        boxes = self.selenium.find_elements_by_css_selector('.white-box')
        self.assertEqual(len(boxes), 3)

        # The first box contains login form elements
        login_box = boxes[0]
        login_title = login_box.find_element_by_tag_name('h2')
        self.assertEqual(login_title.text, 'Login')

        form_inputs = login_box.find_elements_by_tag_name('input')
        self.assertEqual(len(form_inputs), 5)

        # the input fields contain placeholders
        username_field = login_box.find_element_by_id('id_username')
        self.assertEqual(
            username_field.get_attribute('placeholder'), 'Username')
        self.assertEqual(login_box.find_element_by_id(
            'id_password').get_attribute('placeholder'), 'Password')

        # check that the username field has the focus
        self.assertEqual(self.selenium.switch_to.active_element,
                         username_field)

        # there is a "Login" button
        login_button = login_box.find_element_by_name('submit')
        self.assertEqual(login_button.get_attribute('value'), 'Login')

        # there is a "Register" link
        register_link = login_box.find_element_by_link_text('Register')
        self.assertRegexpMatches(
            register_link.get_attribute('href'),
            r'/auth/register/$')

        # there is a "Password reset" link
        pwreset_link = login_box.find_element_by_link_text(
            'Request a password reset')
        self.assertRegexpMatches(
            pwreset_link.get_attribute('href'),
            r'/auth/password/reset/$')

        # The second box has some information about coffeestats
        self.assertEqual(boxes[1].find_element_by_tag_name('h2').text,
                         'What is coffeestats.org?')

        # The third box tells something about graphs
        graph_box = boxes[2]
        self.assertEqual(graph_box.find_element_by_tag_name('h2').text,
                         'Graphs!')
        examplegraph = graph_box.find_element_by_id('coffeeexample')
        self.assertEqual(examplegraph.tag_name, 'canvas')

        self.check_page_footer()

    def test_imprint_elements(self):
        # The caffeine junkie visits coffeestats.org
        self.selenium.get(self.server_url)

        # He wants to see who made this site and clicks the "Imprint" link
        self.selenium.find_element_by_link_text('Imprint').click()

        self.check_page_header()

        self.assertEqual(len(
            self.selenium.find_elements_by_class_name('white-box')), 1
        )

        self.check_page_footer()
