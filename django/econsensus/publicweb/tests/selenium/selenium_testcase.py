from selenium.common.exceptions import NoAlertPresentException,\
    NoSuchElementException
from django.contrib.auth.models import User
from django_selenium.livetestcases import SeleniumLiveTestCase
from publicweb.tests.selenium.pages.base import Login

class SeleniumTestCase(SeleniumLiveTestCase):
    user = None
    
    def login(self, 
        username="test", email="test@fake.com", password="password"):
        if not self.user:
            self.user = self.create_user(username, email, password)
        login = Login(self.driver, {'username': username, 'password': password})
        login.login_with_credentials()
    
    def create_user(self, 
        username="test", email="test@fake.com", password="password"):
        return User.objects.create_user(username, email, password)
    
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
