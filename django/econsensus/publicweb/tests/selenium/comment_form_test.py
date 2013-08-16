from publicweb.tests.selenium.selenium_testcase import SeleniumTestCase
from django_dynamic_fixture import G
from organizations.models import Organization
from guardian.shortcuts import assign_perm
from publicweb.models import Decision, Feedback
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

class CommentFormTest(SeleniumTestCase):
    def setUp(self):
        self.login()
        self.organization = G(Organization)
        self.organization.add_user(self.user)
        assign_perm('edit_decisions_feedback', self.user, self.organization)
    
    def test_comments_form_appears_when_comment_clicked(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        G(Feedback, decision=decision)
                
        driver = self.driver
        driver.get("%s/item/detail/%d/" % (self.live_server_url, decision.id))
        
        driver.find_element_by_css_selector(".show").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_name("comment").is_displayed())
        
        form_css_selector = ".contrib_comment_container > .form_comment > form"
        
        self.assertTrue(
            driver.find_element_by_css_selector(form_css_selector). \
                is_displayed()
                        )
    
    def test_comment_form_cancel_hides_form(self):   
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        G(Feedback, decision=decision)
        
        driver = self.driver
        driver.get("%s/item/detail/%d/" % (self.live_server_url, decision.id))
        
        driver.find_element_by_css_selector(".show").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_name("comment").is_displayed())
             
        driver.find_element_by_css_selector(".controls .button.cancel").click()
        
        form_css_selector = ".contrib_comment_container > .form_comment > form"
        self.assertFalse(
            driver.find_element_by_css_selector(form_css_selector). \
                is_displayed()
            )
    
    def test_clicking_outside_of_form_doesnt_hide_it(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        G(Feedback, decision=decision)
        
        driver = self.driver
        driver.get("%s/item/detail/%d/" % (self.live_server_url, decision.id))
        
        driver.find_element_by_css_selector(".show").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_name("comment").is_displayed())
        
        driver.find_element_by_css_selector("body").click()
        
        form_css_selector = ".contrib_comment_container > .form_comment > form"
    
        self.assertTrue(
                    driver.find_element_by_css_selector(form_css_selector). \
                        is_displayed())
    
    def test_posting_comment_adds_comment_to_feedback(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        G(Feedback, decision=decision)
        
        driver = self.driver
        driver.get("%s/item/detail/%d/" % (self.live_server_url, decision.id))
        
        driver.find_element_by_css_selector(".show").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_name("comment").is_displayed())
        
        driver.find_element_by_name("comment").send_keys("test")
        
        driver.find_element_by_css_selector(".button.go").click()
        
        self.assertTrue(
            self.is_element_present(
                By.CSS_SELECTOR, ".contrib_comment_list .contrib_comment"))
    
    def test_posting_comment_with_invalid_data_displays_errors(self):
        expected_text = ('This field is required.')
        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        G(Feedback, decision=decision)
        
        driver = self.driver
        driver.get("%s/item/detail/%d/" % (self.live_server_url, decision.id))
        
        driver.find_element_by_css_selector(".show").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_name("comment").is_displayed())
        
        driver.find_element_by_css_selector(".button.go").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_css_selector(".errorlist > li"),
            "Check the data being submitted is valid")
        
        actual_text = driver.find_element_by_css_selector(
              ".errorlist > li").text
        
        self.assertEqual(expected_text, actual_text)