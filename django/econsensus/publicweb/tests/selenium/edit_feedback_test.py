from publicweb.tests.selenium.selenium_testcase import SeleniumTestCase
from guardian.shortcuts import assign_perm
from django_dynamic_fixture import G
from organizations.models import Organization
from publicweb.models import Decision, Feedback
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

class EditFeedbackTest(SeleniumTestCase):
    def setUp(self):
        self.login()
        self.organization = G(Organization)
        self.organization.add_user(self.user)
        assign_perm('edit_decisions_feedback', self.user, self.organization)
            
    def test_feedback_form_replaces_edit_link(self):
        # self.selenium is the name of the web driver for the class
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        G(Feedback, decision=decision)
        
        driver = self.driver
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))
        
        driver.find_element_by_css_selector(".description .edit").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_description"))
        
        self.assertTrue(
            self.is_element_present(
                By.CSS_SELECTOR, "li > form"))
        self.assertFalse(
             self.is_element_present(
                 By.CSS_SELECTOR, ".description .edit"))
    
    def test_feedback_form_cancel_recreates_link_without_updating_item(self):        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        G(Feedback, decision=decision)
        
        driver = self.driver
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))
        
        expected_text = driver.find_element_by_css_selector(
              "ol.feedback_list > li").text
        
        driver.find_element_by_css_selector(".description .edit").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_description"))
        
        driver.find_element_by_name('description').send_keys("test")
        
        driver.find_element_by_css_selector(".feedback_cancel").click()

        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_css_selector(".feedback_type"))
        
        actual_text = driver.find_element_by_css_selector(
              "ol.feedback_list > li").text
              
        self.assertTrue(
             self.is_element_present(
                 By.CSS_SELECTOR, ".description .edit"))
        self.assertFalse(
            self.is_element_present(
                By.CSS_SELECTOR, "li > form"))
        self.assertEqual(expected_text, actual_text)
    
    def test_feedback_form_updates_feedback(self):
        expected_text = ('Comment\ntest says:\ntest\nEdit Comment')
        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        driver = self.driver
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))
        
        driver.find_element_by_css_selector("a.button.add_feedback").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_description"))
        
        driver.find_element_by_name('description').send_keys("test")
        
        driver.find_element_by_css_selector(".button.go.once").click()
        
        WebDriverWait(driver, 60).until(
            lambda x: x.find_element_by_css_selector(".button.add_feedback"),
            "Check the data being submitted is valid")
        
        actual_text = driver.find_element_by_css_selector(
              "ol.feedback_list > li").text
        
        self.assertEqual(expected_text, actual_text)
