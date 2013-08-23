from publicweb.tests.selenium.selenium_testcase import SeleniumTestCase
from django_dynamic_fixture import G
from organizations.models import Organization
from guardian.shortcuts import assign_perm
from publicweb.models import Decision
from selenium.webdriver.common.by import By
from publicweb.tests.selenium.pages.decision_detail import FeedbackDetail

class AddFeedbackTypeLinkTest(SeleniumTestCase):
    def setUp(self):
        super(AddFeedbackTypeLinkTest, self).setUp()
        self.login()
        self.organization = G(Organization)
        self.organization.add_user(self.user)
        assign_perm('edit_decisions_feedback', self.user, self.organization)
    
    def test_clicking_on_question_link_adds_form_for_question_feedback(self):
        rating = 'question'
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        decision_page = FeedbackDetail(self.driver, decision)
        
        decision_page.add_feedback_of_type(rating)
        
        self.assertTrue(
            decision_page.is_element_present(
                By.CSS_SELECTOR, decision_page.form_id))
        self.assertFalse(
            decision_page.is_element_present(
                 By.CSS_SELECTOR, ".description .edit"))
        
        selected_option = decision_page.get_select_field_value('rating')

        self.assertEqual(rating, selected_option)
    
    def test_clicking_on_danger_link_adds_form_for_danger_feedback(self):
        rating = "danger"
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        decision_page = FeedbackDetail(self.driver, decision)
        
        decision_page.add_feedback_of_type(rating)
                
        self.assertTrue(
            decision_page.is_element_present(
                By.CSS_SELECTOR, decision_page.form_id))
        self.assertFalse(
             decision_page.is_element_present(
                 By.CSS_SELECTOR, ".description .edit"))
        
        selected_option = decision_page.get_select_field_value('rating')

        self.assertEqual(rating, selected_option)
    
    def test_clicking_on_concerns_link_adds_form_for_concerns_feedback(self):
        rating = "concerns"
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        decision_page = FeedbackDetail(self.driver, decision)
        
        decision_page.add_feedback_of_type(rating)
                
        self.assertTrue(
            decision_page.is_element_present(
                By.CSS_SELECTOR, decision_page.form_id))
        self.assertFalse(
             decision_page.is_element_present(
                 By.CSS_SELECTOR, ".description .edit"))
        
        selected_option = decision_page.get_select_field_value('rating')

        self.assertEqual(rating, selected_option)
    
    def test_clicking_on_consent_link_adds_form_for_consent_feedback(self):
        rating = "consent"
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        decision_page = FeedbackDetail(self.driver, decision)
        
        decision_page.add_feedback_of_type(rating)
                
        self.assertTrue(
            decision_page.is_element_present(
                By.CSS_SELECTOR, decision_page.form_id))
        self.assertFalse(
             decision_page.is_element_present(
                 By.CSS_SELECTOR, ".description .edit"))
        
        selected_option = decision_page.get_select_field_value('rating')

        self.assertEqual(rating, selected_option)
    
    def test_clicking_on_comment_link_adds_form_for_comment_feedback(self):
        rating = "comment"
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        decision_page = FeedbackDetail(self.driver, decision)
        
        decision_page.add_feedback_of_type(rating)
                
        self.assertTrue(
            decision_page.is_element_present(
                By.CSS_SELECTOR, decision_page.form_id))
        self.assertFalse(
             decision_page.is_element_present(
                 By.CSS_SELECTOR, ".description .edit"))
        
        selected_option = decision_page.get_select_field_value('rating')

        self.assertEqual(rating, selected_option)