from django.core.urlresolvers import reverse
from publicweb.tests.decision_test_case import DecisionTestCase

class EditDecisionTest(DecisionTestCase):
   
    def test_edit_description_form_displays_title(self):
        decision = self.create_and_return_decision()
        response = self.load_add_decision_and_return_response(decision.id)
        self.assertContains(response, u"<h2>" + decision.excerpt + \
                            u"</h2>")
    
    def load_add_decision_and_return_response(self, id):
        return self.client.get(reverse('edit_decision', args=[id]))