from open_consent_test_case import OpenConsentTestCase
from publicweb.models import Decision, Feedback
from django.utils.timezone import now
from datetime import date

class DecisionTestCase(OpenConsentTestCase):
    def create_decisions_with_different_statuses(self):
        self.create_and_return_decision(description='Issue Proposal')
        
        self.create_and_return_decision(description='Issue Decision',
                                        status=Decision.DECISION_STATUS)
        
        self.create_and_return_decision(description='Issue Archived',
                                        status=Decision.ARCHIVED_STATUS)

    def create_and_return_example_decision_with_feedback(self):
        decision = self.create_and_return_decision()
        
        feedback = Feedback(description='No time to decide',
                          decision=decision,
                          author=self.user)
        feedback.save()
        
        return decision
    
    def create_and_return_example_concensus_decision_with_feedback(self):
        decision = self.create_and_return_decision(status=Decision.DECISION_STATUS)
        
        feedback = Feedback(description='No time to decide',
                          decision=decision,
                          author=self.user)
        feedback.save()
        
        return decision

    def create_and_return_decision(self, description='Decision Time',
                                   status=Decision.PROPOSAL_STATUS, deadline=now().date()):
        decision = Decision(description=description, status=status, organization=self.bettysorg, deadline=deadline)
        decision.author = self.user
        decision.save()
        
        return decision
