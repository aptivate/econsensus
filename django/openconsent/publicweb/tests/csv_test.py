"""
Tests for the csv export functionality
"""

from publicweb.views import export_csv
from open_consent_test_case import OpenConsentTestCase

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
        # run the function with any old parameter since it doesn't
        # seem to matter
        res = export_csv(1000)  
        self.assertEquals( res.status_code, 200 )
        self.assertEquals( res['Content-Disposition'], 'attachment; filename=publicweb_decision.csv' )
        self.assertEquals( res['Content-Type'],	'text/csv' )
        self.assertTrue( len(res.content) > 0 )


