from django.test import TestCase
from django.contrib.auth.models import User
from mechanize import ParseString

class OpenConsentTestCase(TestCase):
    password_stump = 'password'
    
    def setUp(self):
        User.objects.create_user('Adam', 'adam@openconsent', self.password_stump)
        User.objects.create_user('Barry', 'barry@openconsent', self.password_stump)
        User.objects.create_user('Charlie', 'charlie@openconsent', self.password_stump)
        self.user = self.login('Adam')

    def login(self, user):
        self.client.login(username=user, password=self.password_stump)
        return User.objects.get(username=user) 

    def get_form_values_from_response(self, response, number):
        forms = ParseString(response.content, '')
        
        form_data = {}
        for control in forms[number].controls:
            name = control.name
            form_data[name] = control.value
        
        return form_data
