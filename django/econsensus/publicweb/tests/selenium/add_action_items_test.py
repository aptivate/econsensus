from selenium.webdriver.common.by import By
from django_dynamic_fixture import G
from organizations.models import Organization
from publicweb.models import Decision
from guardian.shortcuts import assign_perm
from selenium.webdriver.support.wait import WebDriverWait
from publicweb.tests.selenium.selenium_testcase import SeleniumTestCase
        
class AddActionItemsTest(SeleniumTestCase):
    def setUp(self):
        self.login()
        self.organization = G(Organization)
        self.organization.add_user(self.user)
        assign_perm('edit_decisions_feedback', self.user, self.organization)
            
    def test_action_item_form_replaces_add_action_item_button(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        driver = self.driver
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))
        
        driver.find_element_by_css_selector("a.button.add_actionitem").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_deadline"))
        
        self.assertTrue(
            self.is_element_present(
                By.CSS_SELECTOR, "#actionitem_add_anchor > form"))
        self.assertFalse(
             self.is_element_present(
                 By.CSS_SELECTOR, "#actionitem_add_anchor > .add_actionitem"))
    
    def test_action_item_form_cancel_recreates_button_without_adding_new_item(self):
        expected_text = "No action items."
        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        driver = self.driver
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))
        
        driver.find_element_by_css_selector("a.button.add_actionitem").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_deadline"))
        
        driver.find_element_by_css_selector(".actionitem_cancel").click()

        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_css_selector("a.button.add_actionitem"))
        
        actual_text = driver.find_element_by_css_selector(
              "ol.actionitem_list > li").text
              
        self.assertTrue(
             self.is_element_present(
                 By.CSS_SELECTOR, "#actionitem_add_anchor > .add_actionitem"))
        self.assertFalse(
            self.is_element_present(
                By.CSS_SELECTOR, "#actionitem_add_anchor > form"))
        self.assertEqual(expected_text, actual_text)
    
    def test_action_item_form_save_with_valid_form_creates_action_item(self):
        expected_text = ('me is responsible for: test\nNo deadline\nEdit')
        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        driver = self.driver
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))
        
        driver.find_element_by_css_selector("a.button.add_actionitem").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_deadline"))
        
        self.driver.find_element_by_name('description').send_keys("test")
        self.driver.find_element_by_name('responsible').send_keys("me")
        
        driver.find_element_by_css_selector(".actionitem_save").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_css_selector("#actionitem_add_anchor"),
            "Check the data being submitted is valid")
        
        actual_text = driver.find_element_by_css_selector(
              "ol.actionitem_list > li").text
        
        self.assertEqual(expected_text, actual_text)

    def test_action_item_form_save_with_invalid_data_displays_errors(self):
        expected_text = ('This field is required.')
        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        driver = self.driver
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))
        
        driver.find_element_by_css_selector("a.button.add_actionitem").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_deadline"))
        
        self.driver.find_element_by_name('description').send_keys("test")
        
        driver.find_element_by_css_selector(".actionitem_save").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_css_selector(".errorlist > li"),
            "Check the data being submitted is valid")
        
        actual_text = driver.find_element_by_css_selector(
              ".errorlist > li").text
        
        self.assertEqual(expected_text, actual_text)
    