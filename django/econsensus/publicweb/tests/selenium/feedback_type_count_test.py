from publicweb.tests.selenium.selenium_testcase import SeleniumTestCase
from django_dynamic_fixture import G
from organizations.models import Organization
from guardian.shortcuts import assign_perm
from publicweb.models import Decision
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select

class FeedbackTypeCountTest(SeleniumTestCase):
    def setUp(self):
        self.login()
        self.organization = G(Organization)
        self.organization.add_user(self.user)
        assign_perm('edit_decisions_feedback', self.user, self.organization)
        
    def test_adding_question_increments_question_count(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        driver = self.selenium
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))
        
        
        link_css_selector = "#decision_detail .stats a dt.question"
        driver.find_element_by_css_selector(link_css_selector).click()
        
        question_count_path = ("//*[@id='decision_detail']//*[@class='stats']/a/"
                             "dt[@class='question']/following-sibling::dd")
        question_element = driver.find_element_by_xpath(question_count_path)
        
        initial_question_count = int(question_element.text)
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_description"))
        
        driver.find_element_by_name('description').send_keys("test")
        selector = Select(driver.find_element_by_name("rating"))
        selector.select_by_visible_text("question")
        
        driver.find_element_by_css_selector(".button.go.once").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_css_selector(".button.add_feedback"),
            "Check the data being submitted is valid")
         
        final_question_count = int(question_element.text)
        
        self.assertGreater(final_question_count, initial_question_count)
 
    def test_adding_danger_increments_danger_count(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        driver = self.selenium
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))
        
        
        link_css_selector = "#decision_detail .stats a dt.danger"
        driver.find_element_by_css_selector(link_css_selector).click()
        danger_count_path = ("//*[@id='decision_detail']//*[@class='stats']/a/"
                             "dt[@class='danger']/following-sibling::dd")
        danger_element = driver.find_element_by_xpath(danger_count_path)
        initial_danger_count = int(danger_element.text)
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_description"))
        
        driver.find_element_by_name('description').send_keys("test")
        selector = Select(driver.find_element_by_name("rating"))
        selector.select_by_visible_text("danger")
        
        driver.find_element_by_css_selector(".button.go.once").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_css_selector(".button.add_feedback"),
            "Check the data being submitted is valid")
         
        final_danger_count = int(danger_element.text)
        
        self.assertGreater(final_danger_count, initial_danger_count)
    
    def test_adding_concerns_increments_concerns_count(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        driver = self.selenium
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))
        
        
        link_css_selector = "#decision_detail .stats a dt.concerns"
        driver.find_element_by_css_selector(link_css_selector).click()
        danger_count_path = ("//*[@id='decision_detail']//*[@class='stats']/a/"
                             "dt[@class='concerns']/following-sibling::dd")
        danger_element = driver.find_element_by_xpath(danger_count_path)
        initial_danger_count = int(danger_element.text)
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_description"))
        
        driver.find_element_by_name('description').send_keys("test")
        selector = Select(driver.find_element_by_name("rating"))
        selector.select_by_visible_text("concerns")
        
        driver.find_element_by_css_selector(".button.go.once").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_css_selector(".button.add_feedback"),
            "Check the data being submitted is valid")
         
        final_danger_count = int(danger_element.text)
        
        self.assertGreater(final_danger_count, initial_danger_count)
    
    def test_adding_consent_increments_consent_count(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        driver = self.selenium
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))
        
        
        link_css_selector = "#decision_detail .stats a dt.consent"
        driver.find_element_by_css_selector(link_css_selector).click()
        danger_count_path = ("//*[@id='decision_detail']//*[@class='stats']/a/"
                             "dt[@class='consent']/following-sibling::dd")
        danger_element = driver.find_element_by_xpath(danger_count_path)
        initial_danger_count = int(danger_element.text)
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_description"))
        
        driver.find_element_by_name('description').send_keys("test")
        selector = Select(driver.find_element_by_name("rating"))
        selector.select_by_visible_text("consent")
        
        driver.find_element_by_css_selector(".button.go.once").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_css_selector(".button.add_feedback"),
            "Check the data being submitted is valid")
         
        final_danger_count = int(danger_element.text)
        
        self.assertGreater(final_danger_count, initial_danger_count)
    
    def test_adding_comment_increments_comment_count(self):
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        driver = self.selenium
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))
        
        
        link_css_selector = "#decision_detail .stats a dt.consent"
        driver.find_element_by_css_selector(link_css_selector).click()
        danger_count_path = ("//*[@id='decision_detail']//*[@class='stats']/a/"
                             "dt[@class='comment']/following-sibling::dd")
        danger_element = driver.find_element_by_xpath(danger_count_path)
        initial_danger_count = int(danger_element.text)
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_description"))
        
        driver.find_element_by_name('description').send_keys("test")
        selector = Select(driver.find_element_by_name("rating"))
        selector.select_by_visible_text("comment")
        
        driver.find_element_by_css_selector(".button.go.once").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_css_selector(".button.add_feedback"),
            "Check the data being submitted is valid")
         
        final_danger_count = int(danger_element.text)
        
        self.assertGreater(final_danger_count, initial_danger_count)