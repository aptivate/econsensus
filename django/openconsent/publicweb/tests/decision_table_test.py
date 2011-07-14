from publicweb.decision_table import DecisionTable
from publicweb.models import Decision
from publicweb.tests.decision_test_case import DecisionTestCase

class DecisionTableTest(DecisionTestCase):
    STATUS_COLUMN = 5
    
    def test_table_has_status_column(self):
        table = DecisionTable(Decision.objects.all())
        
        self.assertTrue("status_text" in table.columns.names())

