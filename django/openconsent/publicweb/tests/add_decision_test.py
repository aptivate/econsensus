from django.core.urlresolvers import reverse
from decision_test_case import DecisionTestCase

class AddDecisionTest(DecisionTestCase):
    def test_jquery_javascript_included_in_page(self):
        response = self.load_add_decision_and_return_response()
        
        self.assertContains(response, "jquery.min.js")
        self.assertContains(response, "jquery-ui.min.js")
        
    def test_jquery_css_included_in_page(self):
        response = self.load_add_decision_and_return_response()
        self.assertContains(response, "jquery-ui.css")

    def test_add_description_form_doesnt_ask_for_name(self):
        response = self.load_add_decision_and_return_response()
        self.assertNotContains(response, "id_short_name")
    
    def load_add_decision_and_return_response(self):
        return self.client.get(reverse('add_decision'))

