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

    #TODO: Needs to work for select elements
    def mechanize_page(self,content):
        forms = ParseString(content, '')
        
        length = len(forms[1].controls)
        form_data = {}
        for control in range(length):
            try:
                 name = forms[1].controls[control].attrs.get("name")
                 if name:
                     if forms[1].controls[control].attrs.get("value") != None:
                         form_data[name]=forms[1].controls[control].attrs.get("value")
                     else:
                         form_data[name]=''

            except AttributeError:
                pass
        
        return form_data
                    
