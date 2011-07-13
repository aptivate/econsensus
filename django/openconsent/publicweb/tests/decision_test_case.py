from publicweb.tests.open_consent_test_case import OpenConsentTestCase
from publicweb.models import Decision, Concern

class DecisionTestCase(OpenConsentTestCase):
    def setUp(self):
        self.login()

    def get_example_decision(self):
        decision = Decision(short_name='Decision Time' )
        decision.save()
        
        concern = Concern(short_name='No time to decide',
                          decision=decision)
        concern.save()
        
        return decision
