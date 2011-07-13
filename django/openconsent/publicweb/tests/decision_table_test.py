from publicweb.tests.open_consent_test_case import OpenConsentTestCase
from publicweb.decision_table import DecisionTable
from publicweb.models import Decision

class DecisionTableTest(OpenConsentTestCase):
    STATUS_COLUMN = 5
    
    def test_table_has_status_column(self):
        table = DecisionTable(Decision.objects.all())
        
        self.assertTrue("status_text" in table.columns.names())
