from publicweb.tests.selenium.selenium_testcase import SeleniumTestCase
from guardian.shortcuts import assign_perm
from django_dynamic_fixture import G
from organizations.models import Organization
from publicweb.models import Decision, Feedback
from selenium.webdriver.common.by import By
from publicweb.tests.selenium.pages.decision_detail import EditFeedbackDetail

class EditFeedbackTest(SeleniumTestCase):
    def setUp(self):
        super(EditFeedbackTest, self).setUp()
        self.login()
        self.organization = G(Organization)
        self.organization.add_user(self.user)
        assign_perm('edit_decisions_feedback', self.user, self.organization)
            
    def test_feedback_form_replaces_edit_link(self):
        # self.selenium is the name of the web driver for the class
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        G(Feedback, decision=decision)
        
        decision_page = EditFeedbackDetail(self.driver, decision)
        decision_page.edit_feedback()
        
        self.assertTrue(
            decision_page.is_element_present(
                By.CSS_SELECTOR, decision_page.form_id))
        self.assertFalse(
            decision_page.is_element_present(
                 By.CSS_SELECTOR, decision_page.edit_link_selector))
    
    def test_feedback_form_cancel_recreates_link_without_updating_item(self):        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        G(Feedback, decision=decision)
        
        decision_page = EditFeedbackDetail(self.driver, decision)
        
        expected_text = decision_page.get_element_text("ol.feedback_list > li")
        decision_page.edit_feedback()
        
        decision_page.update_text_field('description', "test")
        
        decision_page.cancel_changes()
        
        actual_text = decision_page.get_element_text("ol.feedback_list > li")
              
        self.assertTrue(
            decision_page.is_element_present(
                 By.CSS_SELECTOR, decision_page.edit_link_selector))
        self.assertFalse(
            decision_page.is_element_present(
                By.CSS_SELECTOR, decision_page.form_id))
        self.assertEqual(expected_text, actual_text)
    
    def test_feedback_form_updates_feedback(self):
        expected_text = 'Comment\ntest says:\ntest\nEdit Comment'
        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        G(Feedback, decision=decision, author=self.user)
        
        decision_page = EditFeedbackDetail(self.driver, decision)
        
        decision_page.edit_feedback()
        
        decision_page.clear_text_field('description')
        decision_page.update_text_field('description', "test")
                
        decision_page.submit_changes()
        
        actual_text = decision_page.get_element_text("ol.feedback_list > li")
        
        self.assertEqual(expected_text, actual_text)
