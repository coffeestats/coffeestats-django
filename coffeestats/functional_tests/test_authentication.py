from django.core import mail
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from .base import BaseCoffeeStatsPageTestMixin, SeleniumTest


class RegisterUserTest(BaseCoffeeStatsPageTestMixin, SeleniumTest):
    def test_register_tab_order(self):
        self.navigate_to_register_page()

        for inputid in (
            "id_username",
            "id_password1",
            "id_password2",
            "id_email",
            "firstname",
            "lastname",
            "location",
        ):
            nextinput = self.selenium.switch_to.active_element
            self.assertEqual(nextinput.get_attribute("id"), inputid)
            nextinput.send_keys(Keys.TAB)
        lastinput = self.selenium.switch_to.active_element
        self.assertEqual(lastinput.get_attribute("type"), "submit")

    def test_register_input_validation(self):
        self.navigate_to_register_page()

        # he finds the input fields and enters ...
        # ... his desired user name
        input_username = self.selenium.switch_to.active_element
        input_username.send_keys(self.TEST_USERNAME + Keys.TAB)

        input_password1 = self.selenium.switch_to.active_element
        input_password1.send_keys(self.TEST_PASSWORD)

        # he hits enter and gets a validation error
        input_password1.submit()

        input_password1 = self.selenium.find_element_by_id("id_password1")

        elems = input_password1.parent.find_elements_by_css_selector("ul.errorlist")
        self.assertEqual(len(elems), 2)  # one error for email one for password

        # the cursor is on the username input field
        input_username = self.selenium.switch_to.active_element
        self.assertEqual(input_username.get_attribute("id"), "id_username")
        self.assertEqual(input_username.get_attribute("value"), self.TEST_USERNAME)

    def test_register_user(self):
        self.navigate_to_register_page()

        input_username = self.selenium.switch_to.active_element
        input_username.send_keys(self.TEST_USERNAME + Keys.TAB)

        input_password1 = self.selenium.switch_to.active_element
        input_password1.send_keys(self.TEST_PASSWORD + Keys.TAB)

        input_password2 = self.selenium.switch_to.active_element
        input_password2.send_keys(self.TEST_PASSWORD + Keys.TAB)

        input_email = self.selenium.switch_to.active_element
        input_email.send_keys(self.TEST_EMAILADDRESS)

        # he submits the form
        input_email.submit()

        # ... and is redirected to the landing page
        self.assertRegexpMatches(self.selenium.current_url, r"/$")

        # ... and gets an email with an activation link
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Please activate your account", mail.outbox[0].subject)
        self.assertIn(self.TEST_EMAILADDRESS, mail.outbox[0].to)

        activation_link = self.extract_link(mail.outbox[0].body)

        # he opens the activation link
        self.selenium.get(activation_link)

        content = self.selenium.find_element_by_css_selector("body")
        self.assertIn("Your account has been activated successfully.", content.text)

        # he opens the login form and enters his credentials
        header = self.selenium.find_element_by_id("header")
        nav = header.find_element_by_tag_name("nav")
        login_subnav = nav.find_element_by_tag_name("span")
        action_chain = ActionChains(self.selenium)
        action_chain.move_to_element(login_subnav).perform()

        username_field = self.selenium.find_element_by_id("id_login_username")
        username_field.send_keys(self.TEST_USERNAME + Keys.TAB)

        password_field = self.selenium.switch_to.active_element
        self.assertEqual(password_field.get_attribute("id"), "id_login_password")
        password_field.send_keys(self.TEST_PASSWORD + Keys.ENTER)

        # ... and is redirected to the timezone selection page
        self.assertRegexpMatches(
            self.selenium.current_url, r"/selecttimezone/\?next=%2Fprofile%2F$"
        )

        # he selects a time zone
        tzselect = self.selenium.find_element_by_id("tzselect")
        action_chain = ActionChains(self.selenium)
        action_chain.move_to_element(tzselect).perform()

        # submits the form
        submit_button = self.selenium.find_element_by_id("submit")
        submit_button.click()

        # and is redirected to the profile page
        self.assertRegexpMatches(self.selenium.current_url, r"/profile/$")

    def test_forget_password(self):
        self.register_user()

        # find the logout link
        menuitems = self.selenium.find_elements_by_css_selector("#header nav > ul > li")

        self.assertEqual(len(menuitems), 5)

        action_chain = ActionChains(self.selenium)
        action_chain.move_to_element(menuitems[3]).perform()

        # ... and logout
        self.selenium.find_element_by_link_text("Logout").click()

        # find the login form and click the forgot password link
        login_subnav = self.selenium.find_element_by_css_selector(
            "#header nav ul > li > span"
        )
        action_chain = ActionChains(self.selenium)
        action_chain.move_to_element(login_subnav).perform()
        self.selenium.find_element_by_link_text("Forgot your password?").click()

        # check the URL
        self.assertRegexpMatches(self.selenium.current_url, r"/auth/password/reset/$")
        email_field = self.selenium.switch_to.active_element
        self.assertEqual(email_field.get_attribute("id"), "id_email")
        email_field.send_keys(self.TEST_EMAILADDRESS)

        # submits the form
        submit_button = self.selenium.find_element_by_id("submit")
        submit_button.click()

        self.assertRegexpMatches(self.selenium.current_url, r"/password/reset/done/")
        self.assertIn(
            "We sent an email with a password reset link if any of our users"
            " has an account with the given email address.",
            self.selenium.find_element_by_tag_name("body").text,
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.TEST_EMAILADDRESS, mail.outbox[0].to)

        reset_pw_link = self.extract_link(mail.outbox[0].body)
        self.selenium.get(reset_pw_link)

        # we reach the password reset page
        self.assertEqual(
            "Change Your Password", self.selenium.find_element_by_tag_name("h2").text
        )

        pwfield1 = self.selenium.switch_to.active_element
        self.assertEqual(pwfield1.get_attribute("id"), "id_new_password1")
        pwfield1.send_keys(self.TEST_PASSWORD + "new" + Keys.TAB)

        pwfield2 = self.selenium.switch_to.active_element
        self.assertEqual(pwfield2.get_attribute("id"), "id_new_password2")
        pwfield2.send_keys(self.TEST_PASSWORD + "new" + Keys.ENTER)

        self.assertRegexpMatches(
            self.selenium.current_url, r"/password/reset/complete/$"
        )

        # login with the new password
        login_subnav = self.selenium.find_element_by_css_selector(
            "#header nav ul > li > span"
        )
        action_chain = ActionChains(self.selenium)
        action_chain.move_to_element(login_subnav).perform()

        username_field = self.selenium.find_element_by_id("id_login_username")
        username_field.send_keys(self.TEST_USERNAME + Keys.TAB)

        password_field = self.selenium.switch_to.active_element
        self.assertEqual(password_field.get_attribute("id"), "id_login_password")
        password_field.send_keys(self.TEST_PASSWORD + "new" + Keys.ENTER)

        # ... and is redirected to the profile
        self.assertRegexpMatches(self.selenium.current_url, r"/profile/$")
