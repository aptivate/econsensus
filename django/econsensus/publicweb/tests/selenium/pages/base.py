from django.utils.translation import ugettext as _
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

class Base(object):

    def is_element_present(self, how, what):
        try: 
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException: 
            return False
        return True
    
    def get_element_text(self, element, search_method=By.CSS_SELECTOR):
        if self.is_element_present(search_method, element):
            return self.driver.find_element(search_method, element).text
    
    def _wait_for_element(self, element, message=None):
        WebDriverWait(self.driver, 10).until(
            lambda x: x.find_element_by_css_selector(element), message)

class Organizations(Base):
    def __init__(self, driver):
        self.driver = driver
        if self.get_element_text(".page_title") != _("Your Organizations"):
            assert False, "This isn't the organizations list page"
    
    def get_all_organizations_slugs(self):
        """
        Returns an array with the org slugs for the logged in user.
        (Well it should, but it doesn't, right now it just returns smurfs
        need to add class name to org list to make this easy).
        """
        return ['smurfs']

class Login(Base):
    def __init__(self, driver, server_credentials):
        self.driver = driver
        self.username = server_credentials['username']
        self.password = server_credentials['password']
        login_url = "/".join([self.driver.live_server_url, "accounts/login/"])
        self.driver.get(login_url)
        log_in_button_selector = "input[value='%s']" % _('Log in')

        if not self.is_element_present(By.CSS_SELECTOR, log_in_button_selector):
            assert False, "This isn't the login page"
    
    def login_with_credentials(self):
        usernameinput = self.driver.find_element_by_name("username")
        passwordinput = self.driver.find_element_by_name("password")

        # Enter the credentials
        usernameinput.send_keys(self.username)
        passwordinput.send_keys(self.password)

        loginbutton = self.driver.find_element_by_class_name("button")
        loginbutton.click()
        
        self._wait_for_element(".page_title")
        
        return Organizations(self.driver)
    