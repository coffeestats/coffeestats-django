from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

from .base import BaseCoffeeStatsPageTestMixin, SeleniumTest


class BasicPageTest(BaseCoffeeStatsPageTestMixin, SeleniumTest):
    def test_check_homepage_elements(self):
        # Coffeejunkie has heard about coffeestats and wants to visit the
        # homepage
        self.selenium.get(self.server_url)

        self.check_page_header()

        # He sees 2 boxes
        boxes = self.selenium.find_elements(by=By.CSS_SELECTOR, value=".white-box")
        self.assertEqual(len(boxes), 2)

        # The first box is graphs
        graphs_box = boxes[0]
        graphs_title = graphs_box.find_element(by=By.TAG_NAME, value="h2")
        self.assertEqual(graphs_title.text, "Graphs!")
        graphs_box.find_element(by=By.TAG_NAME, value="canvas")

        # The second box is ...
        whatis_box = boxes[1]
        whatis_title = whatis_box.find_element(by=By.TAG_NAME, value="h2")
        self.assertEqual(whatis_title.text, "What is coffeestats.org?")

        # there is a navigation in the page header
        header = self.selenium.find_element(by=By.ID, value="header")
        nav = header.find_element(by=By.TAG_NAME, value="nav")

        # nav contains Register and Login
        register_link = nav.find_element(by=By.LINK_TEXT, value="Register")
        self.assertRegex(register_link.get_attribute("href"), r"/auth/register/$")

        login_subnav = nav.find_element(by=By.TAG_NAME, value="span")
        action_chain = ActionChains(self.selenium)
        action_chain.move_to_element(login_subnav).perform()

        # now a login form is visible
        login_box = nav.find_element(by=By.CSS_SELECTOR, value="ul.loginBox")

        form_inputs = login_box.find_elements(by=By.TAG_NAME, value="input")
        self.assertEqual(len(form_inputs), 5)

        # the input fields contain placeholders
        login_box.find_element(by=By.ID, value="id_login_username")
        username_label = login_box.find_element(
            by=By.CSS_SELECTOR, value='label[for="username"]'
        )
        self.assertEqual(username_label.get_attribute("placeholder"), "Username")

        login_box.find_element(by=By.ID, value="id_login_password")
        password_label = login_box.find_element(
            by=By.CSS_SELECTOR, value='label[for="password"]'
        )
        self.assertEqual(password_label.get_attribute("placeholder"), "Password")

        # there is a "Login" button
        login_button = login_box.find_element(by=By.NAME, value="submit")
        self.assertEqual(login_button.get_attribute("value"), "Login")

        # there is a "Password reset" link
        pwreset_link = login_box.find_element(
            by=By.LINK_TEXT, value="Forgot your password?"
        )
        self.assertRegex(pwreset_link.get_attribute("href"), r"/auth/password/reset/$")

        self.check_page_footer()

    def test_imprint_elements(self):
        # The caffeine junkie visits coffeestats.org
        self.selenium.get(self.server_url)

        # He wants to see who made this site and clicks the "Imprint" link
        self.selenium.find_element(by=By.LINK_TEXT, value="Imprint").click()

        self.check_page_header()

        self.assertEqual(
            len(self.selenium.find_elements(by=By.CLASS_NAME, value="white-box")), 1
        )

        self.check_page_footer()

    def test_overall_elements(self):
        # The caffeine junkie visits coffeestats.org
        self.selenium.get(self.server_url)

        # He sees the Overall link and clicks it
        self.selenium.find_element(by=By.LINK_TEXT, value="Overall").click()

        self.check_page_header()

        # he sees seven white boxes
        graphboxes = self.selenium.find_elements(by=By.CLASS_NAME, value="white-box")
        self.assertEqual(len(graphboxes), 7)

        # the first contains a headline and two paragraphs of text
        self.assertEqual(
            len(graphboxes[0].find_elements(by=By.TAG_NAME, value="h2")), 1
        )
        self.assertEqual(len(graphboxes[0].find_elements(by=By.TAG_NAME, value="p")), 2)

        # the others contain a headline and a graph each
        for box in graphboxes[1:]:
            # check for one headline element
            self.assertEqual(len(box.find_elements(by=By.TAG_NAME, value="h2")), 1)
            # check for one graph element
            self.assertEqual(len(box.find_elements(by=By.TAG_NAME, value="canvas")), 1)

        self.check_page_footer()


class ProfilePageTest(BaseCoffeeStatsPageTestMixin, SeleniumTest):
    def test_redirect_profile_for_anonymous(self):
        self.selenium.get(self.server_url + "/profile/")

        self.check_page_header()

        # He finds out that he was redirected to a login page
        self.assertRegex(self.selenium.current_url, r"/auth/login/\?next=/profile/$")

        # there is a Login form in the page content
        content = self.selenium.find_element(by=By.ID, value="content")
        login_form = content.find_element(by=By.TAG_NAME, value="form")
        # there is a "Login" button
        login_button = login_form.find_element(by=By.NAME, value="submit")
        self.assertEqual(login_button.get_attribute("value"), "Login")

        register_link = content.find_element(by=By.LINK_TEXT, value="Register")
        self.assertRegex(register_link.get_attribute("href"), r"/auth/register/$")

        self.check_page_footer()
