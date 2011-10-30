from django.core.urlresolvers import reverse
from openconsent.publicweb.tests.decision_test_case import DecisionTestCase

#TODO: This class is a bit stumpy... merge with other (web) tests.
class EditDecisionTest(DecisionTestCase):
   
    def test_edit_description_form_displays_title(self):
        decision = self.create_and_return_decision()
        response = self.load_add_decision_and_return_response(decision.id)

        self.assertContains(response, u"<h2 class=\"page_title\">View and Edit: <strong class=\"not_translated\">" + decision.excerpt)

    def load_add_decision_and_return_response(self, id):
        return self.client.get(reverse('edit_decision', args=[id]))