from publicweb.tests.open_consent_test_case import OpenConsentTestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

class LoginTest(OpenConsentTestCase):       
    def test_non_login_is_redirected(self):
        path = reverse('decision_add')
        response = self.client.get(path)
        self.assertEquals(response.status_code, 302)
        
    def test_non_login_directed_to_login_page(self):
        path = reverse('decision_add')
        response = self.client.get(path)
        self.assertRedirects(response, reverse('login')+'?next='+path)

    def test_add_page_loads_when_logged_in(self):
        self.login()
        path = reverse('decision_add')
        response = self.client.get(path)
        self.assertEquals(response.status_code, 200)
        