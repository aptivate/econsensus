from publicweb.tests.decision_test_case import DecisionTestCase
from publicweb.models import Decision
import datetime
from django.core.urlresolvers import reverse
import django_tables
from lxml.html import fromstring
from lxml.cssselect import CSSSelector

class DecisionListPageTest(DecisionTestCase):
    def test_decisions_table_rows_can_be_sorted_by_review_date(self):
        self.assert_decisions_table_sorted_by_date_column('review_date')
        
    def test_descisions_table_rows_can_be_sorted_by_decided_date(self):
        self.assert_decisions_table_sorted_by_date_column('decided_date')

    def test_descisions_table_rows_can_be_sorted_by_expiry_date(self):
        self.assert_decisions_table_sorted_by_date_column('expiry_date')

    def assert_decisions_table_sorted_by_date_column(self, column):
        # Create test decisions in reverse date order.         
        for i in range(5, 0, -1):
            decision = Decision(short_name='Decision %d' % i)
            setattr(decision, column, datetime.date(2001, 3, i))
            decision.save()
            
        response = self.load_decision_list_page_and_return_response(
            data=dict(sort=column))
        decisions_table = response.context['decisions']    
        
        # Check that decision rows are returned in normal order
        rows = list(decisions_table.rows)

        for i in range(1, 6):
            self.assertEquals(datetime.date(2001, 3, i), 
                              getattr(rows[i-1].data, column))

    def test_decisions_table_is_an_instance_of_model_table(self):
        """
        The decisions table is represented using django_tables.ModelTable.
        """
        self.get_example_decision()
        response = self.load_decision_list_page_and_return_response()
        decisions_table = response.context['decisions']
        self.assertTrue(isinstance(decisions_table, django_tables.ModelTable))
    
    def test_status_appears_in_table(self):
        self.get_example_decision()
        response = self.load_decision_list_page_and_return_response()
                
        root = fromstring(response.content)        
        sel = CSSSelector('td')
    
        row_text = []
    
        for element in sel(root):
            row_text.append(element.text)
            
        self.assertTrue("Proposal" in row_text, msg=row_text)
    
    def load_decision_list_page_and_return_response(self, data=None):
        if data is None:
            data = {}
        return self.client.get(reverse('decision_list'), data)
