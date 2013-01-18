import pytest

class TestLogin:

    @pytest.mark.nondestructive
    def test_login(self, mozwebqa):
    
        driver = mozwebqa.selenium
        admin = mozwebqa.credentials['admin']

        # Go to base_url defined in mozwebqa.cfg
        driver.get(mozwebqa.base_url)

        # Enter the credentials
        usernameinput = driver.find_element_by_name("username")
        passwordinput = driver.find_element_by_name("password")

        usernameinput.send_keys(admin['name'])
        passwordinput.send_keys(admin['password'])

        # This is an example of not robust - as soon as another button gets added the wrong one could get clicked
        loginbutton = driver.find_element_by_class_name("button") 
        loginbutton.click()

        driver.find_element_by_partial_link_text('Logout') # Helps the test wait until user is actually logged in  
        assert 'Organization List' in driver.title
