from django.core.exceptions import ValidationError

from publicweb.models import Decision, Feedback
from decision_test_case import DecisionTestCase
from django.contrib.auth.models import User

class ModelTest(DecisionTestCase):

#Generic test functions:
    def model_has_attribute(self, model, attr):
        self.assertTrue(hasattr(model, attr), 
                          "Model %s does not have attribute %s" % (model.__class__,attr))

    def instance_attribute_has_value(self, instance, attr, value):
        target = getattr(instance, attr)
        if callable(target):
            result = target()
        else:
            result = target
            
        self.assertEqual(value, result, 
                          "Attribute %s does not have expected value %s" % (attr,value))

    def instance_validates(self, instance):
        try:
            instance.full_clean()
        except ValidationError, e:
            self.fail("'%s' model instance did not validate: %s" % (instance, e.message_dict))

    def get_column(self, matrix, i):
        return [row[i] for row in matrix]

#The real work:
    def test_decision_has_expected_fields(self):
        decision = self.make_decision()
        self.model_has_attribute(decision, "feedbackcount")
        self.model_has_attribute(decision, "archived_date")
        self.model_has_attribute(decision, "editor")
        self.model_has_attribute(decision, "last_modified")
        self.model_has_attribute(decision, "organization")
        
    def test_watchers_changes(self):
        decision = self.make_decision()
        self.assertEqual(User.objects.count(), decision.watchers.count())

    def test_feedback_can_have_empty_description(self):
        decision = self.make_decision()
        feedback = Feedback(rating=Feedback.CONSENT_STATUS, decision=decision)
        self.instance_validates(feedback)

    def test_model_feedbackcount_changes(self):
        decision = self.make_decision()
        self.instance_attribute_has_value(decision, "feedbackcount", 0)
        feedback = Feedback(description="Feedback test data", decision=decision, author=self.user)
        feedback.save()
        self.instance_attribute_has_value(decision, "feedbackcount", 1)       
        
    def test_feedback_rating_has_values(self):
        expected = ('question', 'danger', 'concerns', 'consent', 'comment')
        names = self.get_column(Feedback.RATING_CHOICES, 1)
        actual = []
        for name in names:
            actual.append(unicode(name))
        
        self.assertEqual(expected, tuple(actual), "Unexpected feedback rating values!")
    
    def test_feedback_has_author(self):
        decision = self.make_decision()
        feedback = Feedback(description="Feedback test data", decision=decision)
        self.model_has_attribute(feedback, "author")

    def test_decision_has_meeting_people(self):
        decision = self.make_decision()
        self.model_has_attribute(decision, "meeting_people")
        
    def test_save_when_no_author(self):
        decision = self.make_decision()
        decision.author = None
        decision.description = "A change."
        try:
            decision.save()
        except:
            self.fail("Failed to save object.")
    
    def test_feedback_statistics(self):
        decision = self.make_decision()
        self.model_has_attribute(decision, "get_feedback_statistics")
        statistics = decision.get_feedback_statistics()
        self.assertTrue("consent" in statistics)
        self.assertTrue("concerns" in statistics)
        self.assertTrue("danger" in statistics)
        self.assertTrue("question" in statistics)
        self.assertTrue("comment" in statistics)
        
        