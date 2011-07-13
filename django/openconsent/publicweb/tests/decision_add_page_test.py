from django.core.urlresolvers import reverse
from publicweb.tests.decision_test_case import DecisionTestCase

class DecisionAddPageTest(DecisionTestCase):
    def test_jquery_javascript_included_in_page(self):
        response = self.load_decision_add_page_and_return_response()
        
        self.assertContains(response, "jquery.min.js")
        self.assertContains(response, "jquery-ui.min.js")
        
    def test_jquery_css_included_in_page(self):
        response = self.load_decision_add_page_and_return_response()
        self.assertContains(response, "jquery-ui.css")

    def test_tiny_mce_javascript_included_in_page(self):
        response = self.load_decision_add_page_and_return_response()
        self.assertContains(response, "tiny_mce.js")

    def load_decision_add_page_and_return_response(self):
        return self.client.get(reverse('decision_add'))
