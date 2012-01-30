from decision_test_case import DecisionTestCase
from django.core.urlresolvers import reverse

class URLTest(DecisionTestCase):

    def test_no_404(self):
        response = self.client.get(reverse('publicweb_item_list', args=['decision']))
        self.assertEqual(response.status_code, 200, "Didn't get 200, got %d. " % response.status_code)
