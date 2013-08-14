from publicweb.tests.selenium.selenium_testcase import SeleniumTestCase
from django_dynamic_fixture import G
from organizations.models import Organization
from guardian.shortcuts import assign_perm
from publicweb.models import Decision
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import time

class AddFeedbackTypeLinkTest(SeleniumTestCase):
    def setUp(self):
        self.login()
        self.organization = G(Organization)
        self.organization.add_user(self.user)
        assign_perm('edit_decisions_feedback',
               self.user, self.organization)
    
    def test_clicking_on_question_link_adds_form_for_question_feedback(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        driver = self.selenium
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))
        
        driver.find_element_by_css_selector("#decision_detail .stats a dt.question").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_description"))
        
        self.assertTrue(
            self.is_element_present(
                By.CSS_SELECTOR, "#feedback_add_anchor > form"))
        self.assertFalse(
             self.is_element_present(
                 By.CSS_SELECTOR, ".description .edit"))
        
        selector = Select(driver.find_element_by_name('rating'))
        selected_option = selector.all_selected_options[0].text

        self.assertEqual("question", selected_option)
    
    def test_clicking_on_danger_link_adds_form_for_danger_feedback(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        driver = self.selenium
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))
        
        driver.find_element_by_css_selector("#decision_detail .stats a dt.danger").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_description"))
        
        self.assertTrue(
            self.is_element_present(
                By.CSS_SELECTOR, "#feedback_add_anchor > form"))
        self.assertFalse(
             self.is_element_present(
                 By.CSS_SELECTOR, ".description .edit"))
        
        selector = Select(driver.find_element_by_name('rating'))
        selected_option = selector.all_selected_options[0].text

        self.assertEqual("danger", selected_option)
    
    def test_clicking_on_concerns_link_adds_form_for_concerns_feedback(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        driver = self.selenium
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))
        
        driver.find_element_by_css_selector("#decision_detail .stats a dt.concerns").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_description"))
        
        self.assertTrue(
            self.is_element_present(
                By.CSS_SELECTOR, "#feedback_add_anchor > form"))
        self.assertFalse(
             self.is_element_present(
                 By.CSS_SELECTOR, ".description .edit"))
        
        selector = Select(driver.find_element_by_name('rating'))
        selected_option = selector.all_selected_options[0].text

        self.assertEqual("concerns", selected_option)
    
    def test_clicking_on_consent_link_adds_form_for_consent_feedback(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        driver = self.selenium
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))
        
        driver.find_element_by_css_selector("#decision_detail .stats a dt.consent").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_description"))
        
        self.assertTrue(
            self.is_element_present(
                By.CSS_SELECTOR, "#feedback_add_anchor > form"))
        self.assertFalse(
             self.is_element_present(
                 By.CSS_SELECTOR, ".description .edit"))
        
        selector = Select(driver.find_element_by_name('rating'))
        selected_option = selector.all_selected_options[0].text

        self.assertEqual("consent", selected_option)
    
    def test_clicking_on_comment_link_adds_form_for_comment_feedback(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        driver = self.selenium
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))
        
        driver.find_element_by_css_selector("#decision_detail .stats a dt.comment").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_description"))
        
        self.assertTrue(
            self.is_element_present(
                By.CSS_SELECTOR, "#feedback_add_anchor > form"))
        self.assertFalse(
             self.is_element_present(
                 By.CSS_SELECTOR, ".description .edit"))
        
        selector = Select(driver.find_element_by_name('rating'))
        selected_option = selector.all_selected_options[0].text

        self.assertEqual("comment", selected_option)