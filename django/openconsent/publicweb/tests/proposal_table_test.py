from publicweb.proposal_table import ProposalTable
from publicweb.models import Decision
from publicweb.tests.decision_test_case import DecisionTestCase

class ProposalTableTest(DecisionTestCase):
    
    def test_table_has_actvity_column(self):
        table = ProposalTable(Decision.objects.all())
        
        self.assertTrue("unresolvedfeedback" in table.columns.names())

