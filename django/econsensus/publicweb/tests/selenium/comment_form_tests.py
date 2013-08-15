from publicweb.tests.selenium.selenium_testcase import SeleniumTestCase
from django_dynamic_fixture import G
from organizations.models import Organization
from guardian.shortcuts import assign_perm
from publicweb.models import Decision, Feedback
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import time

class CommentFormTests(SeleniumTestCase):
    def setUp(self):
        self.login()
        self.organization = G(Organization)
        self.organization.add_user(self.user)
        assign_perm('edit_decisions_feedback', self.user, self.organization)
    
    def test_comments_form_appears_when_comment_clicked(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        G(Feedback, decision=decision)
                
        driver = self.selenium
        driver.get("%s/item/detail/%d/" % (self.live_server_url, decision.id))
        
        driver.find_element_by_css_selector(".show").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_name("comment"))
        
        form_css_selector = ".contrib_comment_container > .form_comment > form"
        
        self.assertTrue(
            self.is_element_present(
                By.CSS_SELECTOR, form_css_selector)
                        )