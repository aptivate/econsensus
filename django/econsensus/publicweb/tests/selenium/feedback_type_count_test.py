from publicweb.tests.selenium.selenium_testcase import SeleniumTestCase
from django_dynamic_fixture import G
from organizations.models import Organization
from guardian.shortcuts import assign_perm
from publicweb.models import Decision, Feedback
from publicweb.tests.selenium.pages.decision_detail import (EditFeedbackDetail, 
    NewFeedbackDetail)

class FeedbackTypeCountTest(SeleniumTestCase):
    def setUp(self):
        super(FeedbackTypeCountTest, self).setUp()
        self.login()
        self.organization = G(Organization)
        self.organization.add_user(self.user)
        assign_perm('edit_decisions_feedback', self.user, self.organization)
        
    def test_adding_question_increments_question_count(self):
        feedback_type = "question"
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        decision_page = NewFeedbackDetail(self.driver, decision)
        
        decision_page.add_feedback_of_type(feedback_type)
        
        initial_question_count = decision_page.get_number_of_feeback_type(
            feedback_type)
        
        decision_page.update_text_field('description', "test")
        decision_page.update_select_field('rating', feedback_type)
        
        decision_page.submit_changes()
         
        final_question_count = decision_page.get_number_of_feeback_type(
            feedback_type)
        
        self.assertGreater(final_question_count, initial_question_count)
 
    def test_adding_danger_increments_danger_count(self):
        feedback_type = "danger"
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        decision_page = NewFeedbackDetail(self.driver, decision)
        
        decision_page.add_feedback_of_type(feedback_type)
        
        initial_danger_count = decision_page.get_number_of_feeback_type(
            feedback_type)
        
        decision_page.update_text_field('description', "test")
        decision_page.update_select_field('rating', feedback_type)
        
        decision_page.submit_changes()
         
        final_danger_count = decision_page.get_number_of_feeback_type(
            feedback_type)
        
        self.assertGreater(final_danger_count, initial_danger_count)
    
    def test_adding_concerns_increments_concerns_count(self):
        feedback_type = "concerns"
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        decision_page = NewFeedbackDetail(self.driver, decision)
        
        decision_page.add_feedback_of_type(feedback_type)
        
        initial_concerns_count = decision_page.get_number_of_feeback_type(
            feedback_type)
        
        decision_page.update_text_field('description', "test")
        decision_page.update_select_field('rating', feedback_type)
        
        decision_page.submit_changes()
         
        final_concerns_count = decision_page.get_number_of_feeback_type(
            feedback_type)
        
        self.assertGreater(final_concerns_count, initial_concerns_count)
    
    def test_adding_consent_increments_consent_count(self):
        feedback_type = "consent"
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        decision_page = NewFeedbackDetail(self.driver, decision)
        
        decision_page.add_feedback_of_type(feedback_type)
        
        initial_consent_count = decision_page.get_number_of_feeback_type(
            feedback_type)
        
        decision_page.update_text_field('description', "test")
        decision_page.update_select_field('rating', feedback_type)
        
        decision_page.submit_changes()
         
        final_consent_count = decision_page.get_number_of_feeback_type(
            feedback_type)

        self.assertGreater(final_consent_count, initial_consent_count)
    
    def test_adding_comment_increments_comment_count(self):
        feedback_type = "comment"
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        decision_page = NewFeedbackDetail(self.driver, decision)
        
        decision_page.add_feedback_of_type(feedback_type)
        
        initial_comment_count = decision_page.get_number_of_feeback_type(
            feedback_type)
        
        decision_page.update_text_field('description', "test")
        decision_page.update_select_field('rating', feedback_type)
        
        decision_page.submit_changes()
         
        final_comment_count = decision_page.get_number_of_feeback_type(
            feedback_type)
        
        self.assertGreater(final_comment_count, initial_comment_count)
        
    def test_changing_question_to_danger_decreases_question_count(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        G(Feedback, rating=Feedback.QUESTION_STATUS, decision=decision)
        decision_page = EditFeedbackDetail(self.driver, decision)
        
        initial_question_count = decision_page.get_number_of_feeback_type(
            'question')
        
        decision_page.edit_feedback()
        
        decision_page.update_text_field('description', "test")
        decision_page.update_select_field('rating', "danger")
        
        decision_page.submit_changes()
         
        final_question_count = decision_page.get_number_of_feeback_type(
            'question')
        
        self.assertLess(final_question_count, initial_question_count)
    
    def test_changing_question_to_danger_increases_danger_count(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        G(Feedback, rating=Feedback.QUESTION_STATUS, decision=decision)
        decision_page = EditFeedbackDetail(self.driver, decision)
        
        initial_danger_count = decision_page.get_number_of_feeback_type(
            'danger')
        
        decision_page.edit_feedback()
        
        decision_page.update_text_field('description', "test")
        decision_page.update_select_field('rating', "danger")
        
        decision_page.submit_changes()
         
        final_danger_count = decision_page.get_number_of_feeback_type(
            'danger')
        
        self.assertGreater(final_danger_count, initial_danger_count)