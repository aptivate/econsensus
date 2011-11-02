from decision_test_case import DecisionTestCase
from publicweb.models import Decision, Feedback

#TODO: Write generic test in the form:
#test_model_has_attribute()
#with a given model and a given attribute
#then farm out function to a generic test suite

class ModelTest(DecisionTestCase):

#Generic test functions:
    def model_has_attribute(self, model, attr):
        self.assertTrue(hasattr(model, attr), 
                          "Model %s does not have attribute %s" % (model,attr))

    def instance_attribute_has_value(self, instance, attr, value):
        target = getattr(instance, attr)
        if callable(target):
            result = target()
        else:
            result = target
            
        self.assertEqual(value, result, 
                          "Attribute %s does not have expected value %s" % (attr,value))

#The real work:
    def test_decision_has_feedbackcount(self):
        self.model_has_attribute(Decision, "feedbackcount")
    
    def test_model_feedbackcount_changes(self):
        decision = Decision(description="Decision test data")
        decision.save(self.user)
        self.instance_attribute_has_value(decision,"feedbackcount",0)
        feedback = Feedback(description="Feedback test data", decision=decision)
        feedback.save()
        self.instance_attribute_has_value(decision,"feedbackcount",1)
        
        
        
