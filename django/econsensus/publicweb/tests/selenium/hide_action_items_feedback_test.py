from django_dynamic_fixture import G
from organizations.models import Organization
from guardian.shortcuts import assign_perm
from publicweb.models import Decision
from publicweb.tests.selenium.selenium_testcase import SeleniumTestCase
from publicweb.tests.selenium.pages.decision_detail import FeedbackDetail
import time

class HideActionItemsFeedbackTest(SeleniumTestCase):
    def setUp(self):
        super(HideActionItemsFeedbackTest, self).setUp()
        self.login()
        self.organization = G(Organization)
        self.organization.add_user(self.user)
        assign_perm('edit_decisions_feedback', self.user, self.organization)
    
    def test_hide_feedback_hides_all_below_title(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)

        decision_page = FeedbackDetail(self.driver, decision)
        decision_page.change_visibility(".page_title.feedback")
        
        self.assertTrue(decision_page.is_element_hidden('#feedback_add_anchor'))
    
    def test_unhide_feedback_shows_all_below_title(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)

        decision_page = FeedbackDetail(self.driver, decision)
        decision_page.change_visibility(".page_title.feedback")
        
        self.assertTrue(decision_page.is_element_hidden('#feedback_add_anchor'))
        
        decision_page.change_visibility(".page_title.feedback")
        self.assertFalse(decision_page.is_element_hidden(
              '#feedback_add_anchor'))
    
    def test_hide_action_item_hides_all_below_title(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)

        decision_page = FeedbackDetail(self.driver, decision)
        
        decision_page.change_visibility(".page_title.actionitem")
        self.assertTrue(
            decision_page.is_element_hidden('#actionitem_add_anchor'))
    
    def test_unhide_action_item_shows_all_below_title(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)

        decision_page = FeedbackDetail(self.driver, decision)
        decision_page.change_visibility(".page_title.actionitem")
        
        self.assertTrue(
             decision_page.is_element_hidden('#actionitem_add_anchor'))
        
        decision_page.change_visibility(".page_title.actionitem")
        
        self.assertFalse(
             decision_page.is_element_hidden('#actionitem_add_anchor'))