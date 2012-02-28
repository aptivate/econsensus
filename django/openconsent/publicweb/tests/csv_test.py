"""
Tests for the csv export functionality
"""

from publicweb.views import export_csv
from open_consent_test_case import OpenConsentTestCase
from django.core.urlresolvers import reverse

class CsvTest(OpenConsentTestCase):
    def test_export_csv(self):
        """
        Tests that export_csv returns a response with:
		Status code 200
		Content-Disposition 'attachment; filename=publicweb_decision.csv'
		Content Length greater than zero.
		TODO:
		Check that when you add or update a decision it is reflected in the output.		      
        """
        path = reverse('publicweb_export_csv')
        response = self.client.get(path)
        self.assertEquals(response.status_code, 200)
        self.assertEquals( response['Content-Disposition'], 'attachment; filename=publicweb_decision.csv' )
        self.assertEquals( response['Content-Type'],	'text/csv' )
        self.assertTrue( len(response.content) > 0 )


