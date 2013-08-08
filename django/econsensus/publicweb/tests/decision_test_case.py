from open_consent_test_case import EconsensusFixtureTestCase
from publicweb.models import Decision, Feedback
from django.utils.timezone import now

class DecisionTestCase(EconsensusFixtureTestCase):
    def create_decisions_with_different_statuses(self):
        self.create_and_return_decision(description='Issue Proposal')
        
        self.create_and_return_decision(description='Issue Decision',
                                        status=Decision.DECISION_STATUS)
        
        self.create_and_return_decision(description='Issue Archived',
                                        status=Decision.ARCHIVED_STATUS)

        self.create_and_return_decision(description='Issue Discussion',
                                        status=Decision.DISCUSSION_STATUS)

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
    
    def create_and_return_feedback(self,decision=None,
                                   description='Feedback', author=None):
        if author==None:
            author=self.user
        if decision==None:
            decision=self.create_and_return_decision()
        feedback = Feedback(description=description,
                          decision=decision,
                          author=author)
        feedback.save()
        return feedback
