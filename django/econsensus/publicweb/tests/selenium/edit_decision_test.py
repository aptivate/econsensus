from publicweb.tests.selenium.selenium_testcase import SeleniumTestCase
from django_dynamic_fixture import G
from publicweb.models import Decision
from organizations.models import Organization
from guardian.shortcuts import assign_perm
from selenium.webdriver.common.by import By
from publicweb.tests.selenium.pages.decision_detail import DecisionDetail

class EditDescisionTest(SeleniumTestCase):
    def setUp(self):
        super(EditDescisionTest, self).setUp()
        self.login()
        self.organization = G(Organization)
        self.organization.add_user(self.user)
        assign_perm('edit_decisions_feedback', self.user, self.organization)
            
    def test_decision_form_replaces_edit_link(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        decision_page = DecisionDetail(self.driver, decision)
        
        decision_page.edit_decision()
        
        self.assertTrue(
            decision_page.is_element_present(
                 By.CSS_SELECTOR, decision_page.form_id))
        self.assertFalse(
             decision_page.is_element_present(
                 By.CSS_SELECTOR, decision_page.replaced_element))
    
    def test_decision_cancel_recreates_decision_without_changes(self):
        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        decision_page = DecisionDetail(self.driver, decision)

        expected_text = decision_page.get_element_text(
              "#decision_detail .description p")
        
        decision_page.edit_decision()
        
        decision_page.update_text_field('description', "test")
        
        decision_page.cancel_changes()
        
        actual_text = decision_page.get_element_text(
              "#decision_detail .description p")
              
        self.assertTrue(
             decision_page.is_element_present(
                 By.CSS_SELECTOR, decision_page.replaced_element))
        self.assertFalse(
            decision_page.is_element_present(
                By.ID, decision_page.desciption_field_id))
        self.assertEqual(expected_text, actual_text)
    
    def test_decision_form_save_with_valid_form_updates_decision(self):        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        expected_text = 'test\nAdded to list by:\n%s\nLast edited by:\n%s' % (
            self.user.username, self.user.username)
        
        decision_page = DecisionDetail(self.driver, decision)
        
        decision_page.edit_decision()
        
        decision_page.clear_text_field('description')
        decision_page.update_text_field('description', "test")
               
        decision_page.submit_changes()
        
        actual_text = decision_page.get_element_text('.description')
        
        self.assertEqual(expected_text, actual_text)

    def test_decision_form_save_with_invalid_data_displays_errors(self):
        expected_text = 'This value is required.'
        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        decision_page = DecisionDetail(self.driver, decision)
        
        decision_page.edit_decision()
           
        decision_page.clear_text_field('description')
        
        decision_page.submit_invalid_changes(decision_page.form_id)
                
        actual_text = decision_page.get_element_text(decision_page.error_list)
        
        self.assertEqual(expected_text, actual_text)