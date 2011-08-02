from publicweb.tests.open_consent_test_case import OpenConsentTestCase
from publicweb.models import Decision, Feedback

class DecisionTestCase(OpenConsentTestCase):
    def setUp(self):
        self.login()
        
    def tearDown(self):
        self.deleteUser()

    def create_decisions_with_different_statuses(self):
        self.create_and_return_decision(short_name='Proposal Decision')
        
        self.create_and_return_decision(short_name='Consensus Decision',
                                        status=Decision.CONSENSUS_STATUS)
        
        self.create_and_return_decision(short_name='Archived Decision',
                                        status=Decision.ARCHIVED_STATUS)

    def create_and_return_example_decision_with_feedback(self):
        decision = self.create_and_return_decision()
        
        feedback = Feedback(short_name='No time to decide',
                          decision=decision)
        feedback.save()
        
        return decision

    def create_and_return_decision(self, short_name='Decision Time',
                                   status=Decision.PROPOSAL_STATUS):
        decision = Decision(short_name=short_name, status=status)
        decision.save()
        
        #decision.add_watcher(self.user)
        #decision.save()

        return decision
