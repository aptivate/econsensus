"""
Tests for the csv export functionality

TODO: Check that when you add or update a decision it is reflected in the output.		      
"""

from open_consent_test_case import EconsensusFixtureTestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from organizations.models import Organization

class CsvTest(EconsensusFixtureTestCase):
    fixtures = ['organizations.json', 'users.json']

    def setUp(self):
        self.test_user = User.objects.get(username="betty")
        self.test_user_org = self.test_user.organization_set.all()[0]
        self.other_org = Organization.objects.exclude(
            id__in=self.test_user.organization_set.values_list('id', flat=True))[0]

    def test_export_csv_not_logged_in(self):
        path = reverse('publicweb_export_csv', args=(self.test_user_org.slug,))
        response = self.client.get(path)
        self.assertEquals(response.status_code, 302)
        self.assertTrue(response.get('Location','').find(
            'login/?next=/%s/export_csv' % self.test_user_org.slug) >= 0)

    def test_export_csv_for_test_user_org(self):
        self.login(self.test_user)
        path = reverse('publicweb_export_csv', args=(self.test_user_org.slug,))
        response = self.client.get(path)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            response['Content-Disposition'], 
            'attachment; filename=econsensus_decision_data_%s.csv' % self.test_user_org.slug
        )
        self.assertEquals(response['Content-Type'],	'text/csv')
        self.assertTrue(len(response.content) > 0)

    def test_export_csv_for_other_org(self):
        self.login(self.test_user)
        path = reverse('publicweb_export_csv', args=(self.other_org.slug,))
        response = self.client.get(path)
        self.assertEquals(response.status_code, 403)


