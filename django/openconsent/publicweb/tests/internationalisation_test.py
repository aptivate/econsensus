from publicweb.tests.open_consent_test_case import OpenConsentTestCase
from django.core.urlresolvers import reverse
from django.utils import translation

class SettingDoesNotExist:
    pass

class InternationalisationTest(OpenConsentTestCase):

    def setUp(self):
        translation.activate('de-AT')
        self.login()
        
    def tearDown(self):
        translation.deactivate()

    #this test needs to check the table's row's heading
    #At the moment mechanize page pulls out form values not row names
    def test_decision_list_changes(self):
        path = reverse('decision_add')
        response = self.client.get(path)
        short_name = response.context['decision_form'].fields['short_name'].label
        self.assertEquals( unicode('Namen'), short_name)
    
