from django.test.testcases import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException,\
    NoAlertPresentException
from django.contrib.auth.models import User

class SeleniumTestCase(LiveServerTestCase):
    user = None
    
    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(SeleniumTestCase, cls).setUpClass()
    
    def login(self, 
        username="test", email="test@fake.com", password="password"):
        if not self.user:
            self.user = self.create_user(username, email, password)
        self.selenium.get(self.live_server_url + "/accounts/login/")
        self.selenium.find_element_by_name('username').send_keys(username)
        self.selenium.find_element_by_name('password').send_keys(password)
        self.selenium.find_element_by_css_selector('[type="submit"]').click()
    
    def create_user(self, 
        username="test", email="test@fake.com", password="password"):
        return User.objects.create_user(username, email, password)
        
    def is_element_present(self, how, what):
        try: 
            self.selenium.find_element(by=how, value=what)
        except NoSuchElementException: 
            return False
        return True
    
    def is_alert_present(self):
        try: 
            self.selenium.switch_to_alert()
        except NoAlertPresentException: 
            return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.selenium.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: 
            self.accept_next_alert = True
    
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(SeleniumTestCase, cls).tearDownClass()
    
