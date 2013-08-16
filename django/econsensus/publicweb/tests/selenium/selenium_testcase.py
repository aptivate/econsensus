from selenium.common.exceptions import NoSuchElementException,\
    NoAlertPresentException
from django.contrib.auth.models import User
from django_selenium.livetestcases import SeleniumLiveTestCase

class SeleniumTestCase(SeleniumLiveTestCase):
    user = None
    
    def login(self, 
        username="test", email="test@fake.com", password="password"):
        if not self.user:
            self.user = self.create_user(username, email, password)
        self.driver.get(self.live_server_url + "/accounts/login/")
        self.driver.find_element_by_name('username').send_keys(username)
        self.driver.find_element_by_name('password').send_keys(password)
        self.driver.find_element_by_css_selector('[type="submit"]').click()
    
    def create_user(self, 
        username="test", email="test@fake.com", password="password"):
        return User.objects.create_user(username, email, password)
        
    def is_element_present(self, how, what):
        try: 
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException: 
            return False
        return True
    
    def is_alert_present(self):
        try: 
            self.driver.switch_to_alert()
        except NoAlertPresentException: 
            return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: 
            self.accept_next_alert = True    
