from django.test import TestCase
from django.contrib.auth.models import User
from mechanize import ParseString

class OpenConsentTestCase(TestCase):
    user = None
    
    def login(self):
        username = 'admin'
        password = 'aptivate'
        email = 'admin@aptivate.org'

        for user in User.objects.all():
            user.delete()
        self.user = User.objects.create_user(username, email, password=password)
        self.user.save()

        self.client.login(username=username, password=password)
        
    def deleteUser(self):
        self.user.delete()

    def get_form_values_from_response(self, response, number):
        forms = ParseString(response.content, '')
        
        form_data = {}
        for control in forms[number].controls:
            name = control.name
            form_data[name]=control.value
        
        return form_data
