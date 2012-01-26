from open_consent_test_case import OpenConsentTestCase
from publicweb.models import Decision, Feedback

class DecisionTestCase(OpenConsentTestCase):
    def setUp(self):
        self.login()
        
    def tearDown(self):
        self.deleteUser()

    def create_decisions_with_different_statuses(self):
        self.create_and_return_decision(description='Issue Proposal')
        
        self.create_and_return_decision(description='Issue Decision',
                                        status=Decision.DECISION_STATUS)
        
        self.create_and_return_decision(description='Issue Archived',
                                        status=Decision.ARCHIVED_STATUS)

    def create_and_return_example_decision_with_feedback(self):
        decision = self.create_and_return_decision()
        
        feedback = Feedback(description='No time to decide',
                          decision=decision)
        feedback.save()
        
        return decision
    
    def create_and_return_example_concensus_decision_with_feedback(self):
        decision = self.create_and_return_decision(status=Decision.DECISION_STATUS)
        
        feedback = Feedback(description='No time to decide',
                          decision=decision)
        feedback.save()
        
        return decision

    def create_and_return_decision(self, description='Decision Time',
                                   status=Decision.PROPOSAL_STATUS):
        decision = Decision(description=description, status=status)
        decision.author = self.user
        decision.save(self.user)
        
        return decision
