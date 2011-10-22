from publicweb.tests.open_consent_test_case import OpenConsentTestCase
from django.core.urlresolvers import reverse

class LoginTest(OpenConsentTestCase):       
    def test_non_login_is_redirected(self):
        path = reverse('add_decision')
        response = self.client.get(path)
        self.assertEquals(response.status_code, 302)
        
    def test_non_login_directed_to_login(self):
        path = reverse('add_decision')
        response = self.client.get(path)
        self.assertRedirects(response, reverse('login')+'?next='+path)

    def test_add_decision_loads_when_logged_in(self):
        self.login()
        path = reverse('add_decision')
        response = self.client.get(path)
        self.assertEquals(response.status_code, 200)
        
    def test_can_post_through_login(self):
        path = reverse('login')
        page = self.client.get(path)
        
        post_data = self.get_form_values_from_response(page, 1)
        self.assertIn('username', post_data, 'No username field in page content!')
        self.assertIn('password', post_data, 'No password field in page content!')
        post_data['login'] = 'admin'
        post_data['password'] = 'aptivate'
                
        #post_data.update(feedback_formset.management_form.initial)
        self.client.post(path, post_data, follow=True)

        path = reverse('add_decision')
        response = self.client.get(path, follow=True)
        self.assertEquals(response.status_code, 200)
