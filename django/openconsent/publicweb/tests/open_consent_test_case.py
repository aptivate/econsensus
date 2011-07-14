from django.test import TestCase
from django.contrib.auth.models import User
from mechanize import ParseString

class OpenConsentTestCase(TestCase):
    def login(self):
        username = 'admin'
        password = 'aptivate'
        email = 'admin@aptivate.org'
        user = User.objects.create_user(username, email, password=password)
        user.save()
        self.client.login(username=username, password=password)

    def get_form_values_from_response(self, response):
        forms = ParseString(response.content, '')
        
        form_data = {}
        for control in forms[1].controls:
            name = control.name
            form_data[name]=control.value
        
        return form_data
