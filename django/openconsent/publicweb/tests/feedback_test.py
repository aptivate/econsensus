from publicweb.tests.decision_test_case import DecisionTestCase

class FeedbackTest(DecisionTestCase):

    def test_feedback_has_rating(self):
        decision = self.create_and_return_example_decision_with_feedback()
    
        feedback = decision.feedback_set.all()[0]
        self.assertEquals(True, hasattr(feedback, "rating"), 
                          "Concern does not have a 'rating' attribute")
    