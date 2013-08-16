from django_dynamic_fixture import G
from organizations.models import Organization
from guardian.shortcuts import assign_perm
from publicweb.models import Decision
from publicweb.tests.selenium.selenium_testcase import SeleniumTestCase

class HideActionItemsFeedbackTest(SeleniumTestCase):
    def setUp(self):
        self.login()
        self.organization = G(Organization)
        self.organization.add_user(self.user)
        assign_perm('edit_decisions_feedback', self.user, self.organization)
    
    def test_hide_feedback_hides_all_below_title(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)

        driver = self.driver
        driver.get("%s/item/detail/%d/" % (self.live_server_url, decision.id))
        
        self.driver.find_element_by_css_selector(".page_title.feedback").click()
        self.assertFalse(self.driver.find_element_by_css_selector(
              '#feedback_add_anchor').is_displayed())
    
    def test_unhide_feedback_shows_all_below_title(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)

        driver = self.driver
        driver.get("%s/item/detail/%d/" % (self.live_server_url, decision.id))
        
        self.driver.find_element_by_css_selector(".page_title.feedback").click()
        self.assertFalse(self.driver.find_element_by_css_selector(
              '#feedback_add_anchor').is_displayed())
        
        self.driver.find_element_by_css_selector(".page_title.feedback").click()
        
        self.assertTrue(self.driver.find_element_by_css_selector(
              '#feedback_add_anchor').is_displayed())
    
    def test_hide_action_item_hides_all_below_title(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)

        driver = self.driver
        driver.get("%s/item/detail/%d/" % (self.live_server_url, decision.id))
        
        self.driver.find_element_by_css_selector(".page_title.actionitem").click()
        self.assertFalse(self.driver.find_element_by_css_selector(
              '#actionitem_add_anchor').is_displayed())
    
    def test_unhide_action_item_shows_all_below_title(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)

        driver = self.driver
        driver.get("%s/item/detail/%d/" % (self.live_server_url, decision.id))
        
        self.driver.find_element_by_css_selector(".page_title.actionitem").click()
        self.assertFalse(self.driver.find_element_by_css_selector(
              '#actionitem_add_anchor').is_displayed())
        
        self.driver.find_element_by_css_selector(".page_title.actionitem").click()
        
        self.assertTrue(self.driver.find_element_by_css_selector(
              '#actionitem_add_anchor').is_displayed())