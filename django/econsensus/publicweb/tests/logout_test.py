from open_consent_test_case import EconsensusTestCase
from django.core.urlresolvers import reverse
from publicweb.models import Decision

class LogoutTest(EconsensusTestCase):       
    def test_logout_is_redirected(self):
        path = reverse('publicweb_decision_create', args=[self.bettysorg.slug, Decision.PROPOSAL_STATUS])
        self.client.get(path, follow=True)
        path = reverse('auth_logout')
        response = self.client.get(path, follow=True)
        self.assertEquals(response.status_code, 200)