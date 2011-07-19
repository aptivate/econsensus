from django.core.urlresolvers import reverse
from publicweb.tests.decision_test_case import DecisionTestCase

class FeedbackTest(DecisionTestCase):

    def load_decision_add_page_and_return_response(self):
        return self.client.get(reverse('decision_add'))

    