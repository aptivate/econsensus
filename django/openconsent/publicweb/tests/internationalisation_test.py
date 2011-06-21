from publicweb.tests.open_consent_test_case import OpenConsentTestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings
from mechanize import ParseString
from contextlib import contextmanager

class SettingDoesNotExist:
    pass

class InternationalisationTest(OpenConsentTestCase):

    @contextmanager
    def patch_settings(**kwargs):
        from django.conf import settings
        old_settings = []
        for key, new_value in kwargs.items():
            old_value = getattr(settings, key, SettingDoesNotExist)
            old_settings.append((key, old_value))
            setattr(settings, key, new_value)
        yield
        for key, old_value in old_settings:
            if old_value is SettingDoesNotExist:
                delattr(settings, key)
            else:
                setattr(settings, key, old_value)

    def setUp(self):
        self.patch_settings(MY_SETTING='my value')
        self.login()
        
    def tearDown(self):
       print "***Language at tear down: ", settings.LANGUAGE_CODE
           
    #this test needs to check the table's row's heading
    #At the moment mechanize page pulls out form values not row names
    def test_decision_list_changes(self):
        print "Language Code: ", settings.LANGUAGE_CODE
        
        path = reverse('decision_add')
        page = self.client.get(path)

        forms = ParseString(page.content, '')

        print "***Context Label: ", page.context['decision_form'].fields['short_name'].label        
        print "***Form Label: ", forms[1].controls[0].get_labels()[0].text

        short_name = page.context['decision_form'].fields['short_name'].label
        
        self.assertEquals( unicode('Namen'), short_name)
        
