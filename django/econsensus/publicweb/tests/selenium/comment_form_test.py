from publicweb.tests.selenium.selenium_testcase import SeleniumTestCase
from django_dynamic_fixture import G
from organizations.models import Organization
from guardian.shortcuts import assign_perm
from publicweb.models import Decision, Feedback
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from publicweb.tests.selenium.pages.decision_detail import CommentDetail

class CommentFormTest(SeleniumTestCase):
    def setUp(self):
        super(CommentFormTest, self).setUp()
        self.login()
        self.organization = G(Organization)
        self.organization.add_user(self.user)
        assign_perm('edit_decisions_feedback', self.user, self.organization)
    
    def test_comments_form_appears_when_comment_clicked(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        G(Feedback, decision=decision)
        
        decision_page = CommentDetail(self.driver, decision)
        
        decision_page.add_comment()
        
        self.assertTrue(
            decision_page.is_element_displayed(
               By.CSS_SELECTOR, decision_page.form_id))
    
    def test_comment_form_cancel_hides_form(self):   
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        G(Feedback, decision=decision)
        
        decision_page = CommentDetail(self.driver, decision)
        
        decision_page.add_comment()
        
        decision_page.cancel_changes()
             
        self.assertFalse(
            decision_page.is_element_displayed(
               By.CSS_SELECTOR, decision_page.form_id)
            )
    
    def test_clicking_outside_of_form_doesnt_hide_it(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        G(Feedback, decision=decision)
        
        decision_page = CommentDetail(self.driver, decision)
        
        decision_page.add_comment()
        
        decision_page.click_outside_form()
        
        self.assertTrue(
            decision_page.is_element_displayed(
               By.CSS_SELECTOR, decision_page.form_id))
    
    def test_posting_comment_adds_comment_to_feedback(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        G(Feedback, decision=decision)
        
        decision_page = CommentDetail(self.driver, decision)
        
        decision_page.add_comment()
        
        decision_page.update_text_field('comment', "test")
        
        decision_page.submit_changes()
        
        self.assertTrue(
            decision_page.is_element_present(
                By.CSS_SELECTOR, ".contrib_comment_list .contrib_comment"))
    
    def test_posting_comment_with_invalid_data_displays_errors(self):
        expected_text = ('This value is required.')
        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        G(Feedback, decision=decision)
        
        
        decision_page = CommentDetail(self.driver, decision)
        
        decision_page.add_comment()
                
        decision_page.submit_invalid_changes(decision_page.form_id)
        
        actual_text = decision_page.get_element_text(decision_page.error_list)
        
        self.assertEqual(expected_text, actual_text)