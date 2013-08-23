from selenium.webdriver.common.by import By
from django_dynamic_fixture import G
from organizations.models import Organization
from publicweb.models import Decision
from guardian.shortcuts import assign_perm
from publicweb.tests.selenium.selenium_testcase import SeleniumTestCase
from publicweb.tests.selenium.pages.decision_detail import DecisionDetail,\
    NewActionitemDetail
        
class AddActionItemsTest(SeleniumTestCase):
    def setUp(self):
        super(AddActionItemsTest, self).setUp()
        self.login()
        self.organization = G(Organization)
        self.organization.add_user(self.user)
        assign_perm('edit_decisions_feedback', self.user, self.organization)
            
    def test_action_item_form_replaces_add_action_item_button(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
       
        decision_page = NewActionitemDetail(self.driver, decision)
        
        decision_page.add_actionitem()
        
        self.assertTrue(
            decision_page.is_element_present(
                By.CSS_SELECTOR, "#actionitem_add_anchor > form"))
        self.assertFalse(
             decision_page.is_element_present(
                 By.CSS_SELECTOR, "#actionitem_add_anchor > .add_actionitem"))
    
    def test_action_item_form_cancel_recreates_button_without_adding_new_item(self):
        expected_text = "No action items."
        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        decision_page = NewActionitemDetail(self.driver, decision)
        
        decision_page.add_actionitem()
        
        decision_page.cancel_changes()
        
        actual_text = decision_page.get_element_text("ol.actionitem_list > li")
              
        self.assertTrue(
             decision_page.is_element_present(
                 By.CSS_SELECTOR, decision_page.edit_link_selector))
        self.assertFalse(
            decision_page.is_element_present(
                By.CSS_SELECTOR, decision_page.form_id))
        self.assertEqual(expected_text, actual_text)
    
    def test_action_item_form_cancel_only_closes_actionitem_form(self):
        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        decision_page = NewActionitemDetail(self.driver, decision)
        
        decision_page.edit_decision()
        decision_page.add_actionitem()

        decision_page.cancel_changes()
              
        self.assertTrue(
             decision_page.is_element_present(
                 By.CSS_SELECTOR, DecisionDetail.form_id))
        self.assertFalse(
            decision_page.is_element_present(
                By.CSS_SELECTOR, decision_page.form_id))
    
    def test_action_item_form_save_with_valid_form_creates_action_item(self):
        expected_text = ('me is responsible for: test\nNo deadline\nEdit')
        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        decision_page = NewActionitemDetail(self.driver, decision)
        
        decision_page.add_actionitem()
        
        decision_page.update_text_field('description', "test")
        decision_page.update_text_field('responsible', "me")
                
        decision_page.submit_changes()
        
        actual_text = decision_page.get_element_text('ol.actionitem_list > li')
        
        self.assertEqual(expected_text, actual_text)

    def test_action_item_form_save_with_invalid_data_displays_errors(self):
        expected_text = 'This value is required.'
        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        decision_page = NewActionitemDetail(self.driver, decision)
        
        decision_page.add_actionitem()
        
        decision_page.update_text_field('description', "test")
        
        decision_page.submit_invalid_changes(decision_page.form_id)
        
        actual_text = decision_page.get_element_text('.parsley-error-list > li')
        
        self.assertEqual(expected_text, actual_text)
    