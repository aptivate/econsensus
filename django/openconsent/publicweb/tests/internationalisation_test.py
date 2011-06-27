# coding: utf-8

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
    #requires compiled django translation to be present
    def assert_decision_list_translation(self,raw_field, translated_field):
        path = reverse('decision_add')
        response = self.client.get(path)
        name = response.context['decision_form'].fields[raw_field].label
        self.assertEquals( unicode(translated_field), name)
        
    def test_translation_decided_date(self):
        translation_dictionary = {'short_name' : 'Namen',
                                  'decided_date': 'Entschiedenes Datum',
                                  'effective_date' : unicode('Tatsächliches Datum', 'utf8'),
                                  'review_date' : 'Berichtdatum',
                                  'expiry_date' : 'Verfallsdatum',
                                  'budget' : 'Etat',
                                  'people' : 'Leute',
                                  'description' : 'Beschreibung'                                  
                                   }
        
        for (key, value) in translation_dictionary.iteritems():
            self.assert_decision_list_translation(key,value)
                
