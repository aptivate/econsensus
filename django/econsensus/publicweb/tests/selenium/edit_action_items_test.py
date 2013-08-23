from publicweb.tests.selenium.selenium_testcase import SeleniumTestCase
from django_dynamic_fixture import G
from publicweb.models import Decision
from organizations.models import Organization
from guardian.shortcuts import assign_perm
from selenium.webdriver.common.by import By
from actionitems.models import ActionItem
from django.utils.formats import date_format
from publicweb.tests.selenium.pages.decision_detail import EditActionitemDetail,\
    DecisionDetail

class EditActionItemsTest(SeleniumTestCase):
    def setUp(self):
        super(EditActionItemsTest, self).setUp()
        self.login()
        self.organization = G(Organization)
        self.organization.add_user(self.user)
        assign_perm('edit_decisions_feedback', self.user, self.organization)
            
    def test_action_item_form_replaces_edit_link(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        G(ActionItem, origin=decision)
        
        decision_page = EditActionitemDetail(self.driver, decision)
        decision_page.edit_actionitem()
        
        self.assertTrue(
            decision_page.is_element_present(
                By.CSS_SELECTOR, decision_page.form_id))
        self.assertFalse(
            decision_page.is_element_present(
                 By.CSS_SELECTOR, decision_page.replaced_element))
    
    def test_action_item_form_cancel_recreates_item_without_changes(self):
        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        G(ActionItem, origin=decision)
        
        decision_page = EditActionitemDetail(self.driver, decision)

        expected_text = decision_page.get_element_text(
           "ol.actionitem_list > li")
        
        decision_page.edit_actionitem()
        
        decision_page.update_text_field('description', "test")
        
        decision_page.cancel_changes()

        actual_text = decision_page.get_element_text(
              "ol.actionitem_list > li")
        
        self.assertTrue(
            decision_page.is_element_present(
                 By.CSS_SELECTOR, 
                 ".actionitem_list > li > .actionitem_feedback_wrapper"))
        self.assertFalse(
            decision_page.is_element_present(
                By.CSS_SELECTOR, decision_page.form_id))
        self.assertEqual(expected_text, actual_text)
    
    def test_action_item_form_cancel_only_closes_action_item_form(self):
        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        G(ActionItem, origin=decision)
        
        decision_page = EditActionitemDetail(self.driver, decision)

        decision_page.edit_decision()
        decision_page.edit_actionitem()
        
        decision_page.update_text_field('description', "test")
        
        decision_page.cancel_changes()
        
        self.assertTrue(
            decision_page.is_element_present(
                 By.CSS_SELECTOR, DecisionDetail.form_id))
        self.assertFalse(
            decision_page.is_element_present(
                By.CSS_SELECTOR, decision_page.form_id))
    
    def test_action_item_form_save_with_valid_form_updates_action_item(self):        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        action_item = G(ActionItem, origin=decision)
        
        expected_text = 'me is responsible for: test\nby %s\nEdit' % (
            date_format(action_item.deadline, "DATE_FORMAT"))
        
        decision_page = EditActionitemDetail(self.driver, decision)
        decision_page.edit_actionitem()
        decision_page.clear_text_field('description')
        decision_page.clear_text_field('responsible')
        decision_page.update_text_field('description', "test")
        decision_page.update_text_field('responsible', "me")
        
        decision_page.submit_changes()

        actual_text = decision_page.get_element_text(
         decision_page.replaced_element)
        
        self.assertEqual(expected_text, actual_text)

    def test_action_item_form_save_with_invalid_data_displays_errors(self):
        expected_text = ('This value is required.')
        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        G(ActionItem, origin=decision)
        
        decision_page = EditActionitemDetail(self.driver, decision)
        decision_page.edit_actionitem()
        
        decision_page.clear_text_field('description')
        
        decision_page.submit_invalid_changes(decision_page.form_id)
        
        actual_text = decision_page.get_element_text(decision_page.error_list)
        
        self.assertEqual(expected_text, actual_text)