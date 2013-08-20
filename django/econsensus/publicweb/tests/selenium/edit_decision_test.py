from publicweb.tests.selenium.selenium_testcase import SeleniumTestCase
from django_dynamic_fixture import G
from publicweb.models import Decision
from organizations.models import Organization
from guardian.shortcuts import assign_perm
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from actionitems.models import ActionItem
from django.utils.formats import date_format

class EditDescisionTest(SeleniumTestCase):
    def setUp(self):
        self.login()
        self.organization = G(Organization)
        self.organization.add_user(self.user)
        assign_perm('edit_decisions_feedback', self.user, self.organization)
            
    def test_decision_form_replaces_edit_link(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        driver = self.driver
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))
        
        driver.find_element_by_css_selector(".controls .edit").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_description"))
        
        self.assertTrue(
            self.is_element_present(
                By.CSS_SELECTOR, "#decision_update_form"))
        self.assertFalse(
             self.is_element_present(
                 By.CSS_SELECTOR, "#decision_snippet_envelope .page_title"))
    
    def test_decision_cancel_recreates_decision_without_changes(self):
        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        driver = self.driver
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))

        expected_text = driver.find_element_by_css_selector(
              "#decision_detail .description p").text
        
        driver.find_element_by_css_selector(".controls .edit").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_description"))
        
        self.driver.find_element_by_name('description').send_keys("test")
        
        driver.find_element_by_css_selector(
            "#decision_update_form input[value=\"Cancel\"]").click()

        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_css_selector(
                 "#decision_snippet_envelope .page_title"),
            "Check the data being submitted is valid")
        
        actual_text = driver.find_element_by_css_selector(
              "#decision_detail .description p").text
              
        self.assertTrue(
             self.is_element_present(
                 By.CSS_SELECTOR, "#decision_snippet_envelope .page_title"))
        self.assertFalse(
            self.is_element_present(
                By.CSS_SELECTOR, "#id_description"))
        self.assertEqual(expected_text, actual_text)
    
    def test_decision_form_save_with_valid_form_updates_decision(self):        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        expected_text = 'test\nAdded to list by:\n%s\nLast edited by:\n%s' % (
            self.user.username, self.user.username)
        
        driver = self.driver
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))
        
        driver.find_element_by_css_selector(".controls .edit").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_description"))
        
        self.driver.find_element_by_name('description').clear()
        self.driver.find_element_by_name('description').send_keys("test")
        
        driver.find_element_by_css_selector(
            "#decision_update_form input[value=\"Save\"]").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_css_selector(
                 "#decision_snippet_envelope .page_title"),
            "Check the data being submitted is valid")
        
        actual_text = driver.find_element_by_css_selector(
              ".description").text
        
        self.assertEqual(expected_text, actual_text)

    def test_decision_form_save_with_invalid_data_displays_errors(self):
        expected_text = ('This field is required.')
        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        driver = self.driver
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))
        
        driver.find_element_by_css_selector(".controls .edit").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_description"))
        
        self.driver.find_element_by_name('description').clear()
        
        driver.find_element_by_css_selector(
            "#decision_update_form input[value=\"Save\"]").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_css_selector(".errorlist > li"))
        
        actual_text = driver.find_element_by_css_selector(
              ".parsley-error-list > li").text
        
        self.assertEqual(expected_text, actual_text)