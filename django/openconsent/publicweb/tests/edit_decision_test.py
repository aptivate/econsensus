from django.core.urlresolvers import reverse
from decision_test_case import DecisionTestCase

#TODO: This class is a bit stumpy... merge with other (web) tests.
class EditDecisionTest(DecisionTestCase):
   
    def test_edit_description_form_displays_title(self):
        decision = self.create_and_return_decision()
        response = self.load_add_decision_and_return_response(decision.id)
        self.assertContains(response, u"Update Decision #%s" % decision.id)

    def load_add_decision_and_return_response(self, idd):
        return self.client.get(reverse('publicweb_decision_update', args=[idd]))