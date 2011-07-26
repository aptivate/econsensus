from django.core.urlresolvers import reverse
from publicweb.tests.decision_test_case import DecisionTestCase

class AddDecisionTest(DecisionTestCase):
    def test_jquery_javascript_included_in_page(self):
        response = self.load_add_decision_and_return_response()
        
        self.assertContains(response, "jquery.min.js")
        self.assertContains(response, "jquery-ui.min.js")
        
    def test_jquery_css_included_in_page(self):
        response = self.load_add_decision_and_return_response()
        self.assertContains(response, "jquery-ui.css")

    def test_tiny_mce_javascript_included_in_page(self):
        response = self.load_add_decision_and_return_response()
        self.assertContains(response, "tiny_mce.js")

    def load_add_decision_and_return_response(self):
        return self.client.get(reverse('add_decision'))
