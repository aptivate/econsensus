from publicweb.tests.selenium.selenium_testcase import SeleniumTestCase
from guardian.shortcuts import assign_perm
from django_dynamic_fixture import G
from organizations.models import Organization
from publicweb.models import Decision
from selenium.webdriver.common.by import By
from publicweb.tests.selenium.pages.decision_detail import NewFeedbackDetail

class AddFeedbackTest(SeleniumTestCase):
    def setUp(self):
        super(AddFeedbackTest, self).setUp()
        self.login()
        self.organization = G(Organization)
        self.organization.add_user(self.user)
        assign_perm('edit_decisions_feedback', self.user, self.organization)
            
    def test_feedback_form_replaces_add_feedback_button(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        decision_page = NewFeedbackDetail(self.driver, decision)
        
        decision_page.add_feedback_item()
        
        self.assertTrue(
            decision_page.is_element_present(
                By.CSS_SELECTOR, "#feedback_add_anchor > form"))
        self.assertFalse(
             decision_page.is_element_present(
                 By.CSS_SELECTOR, "#feedback_add_anchor > .add_feedback"))
    
    def test_feedback_form_cancel_recreates_button_without_adding_new_item(self):
        expected_text = "No feedback yet."
        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        decision_page = NewFeedbackDetail(self.driver, decision)
        
        decision_page.add_feedback_item()
        decision_page.cancel_changes()
                
        actual_text = decision_page.get_element_text("ol.feedback_list > li")
              
        self.assertTrue(
             decision_page.is_element_present(
                 By.CSS_SELECTOR, decision_page.replaced_element))
        self.assertFalse(
            decision_page.is_element_present(
                By.CSS_SELECTOR, decision_page.form_id))
        self.assertEqual(expected_text, actual_text)
    
    def test_feedback_form_save_creates_feedback(self):
        expected_text = ('Consent\ntest says:\ntest\nEdit Comment')
        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        decision_page = NewFeedbackDetail(self.driver, decision) 
        
        decision_page.add_feedback_item()
        
        decision_page.update_text_field('description', "test")
        decision_page.update_select_field('rating', "consent")
        
        decision_page.submit_changes()
        
        actual_text = decision_page.get_element_text("ol.feedback_list > li")
        
        self.assertEqual(expected_text, actual_text)
