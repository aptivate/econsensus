from open_consent_test_case import OpenConsentTestCase
from django.core.urlresolvers import reverse
from publicweb.models import Decision

class LogoutTest(OpenConsentTestCase):       
    def test_logout_is_redirected(self):
        path = reverse('publicweb_decision_create', args=[Decision.PROPOSAL_STATUS])
        self.client.get(path, follow=True)
        path = reverse('logout')
        response = self.client.get(path, follow=True)
        self.assertEquals(response.status_code, 200)