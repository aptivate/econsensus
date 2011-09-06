from publicweb.tests.decision_test_case import DecisionTestCase
from publicweb.models import Decision
import datetime
from django.core.urlresolvers import reverse
import django_tables
from lxml.html import fromstring
from lxml.cssselect import CSSSelector

class DecisionListTest(DecisionTestCase):
    
    def test_status_filter_form(self):
        self.create_decisions_with_different_statuses()
        
        path = reverse('decision_list')
        page = self.client.get(path)
        
        get_data = self.get_form_values_from_response(page)
        get_data['status'] = Decision.PROPOSAL_STATUS
        response = self.client.get(path, get_data)

        self.check_cell_text_appears_in_table(response, "Proposal Decision")
        self.check_cell_text_does_not_appear_in_table(response, "Consensus Decision")
        self.check_cell_text_does_not_appear_in_table(response, "Archived Decision")

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
            decision.save(self.user)
            
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
        self.create_and_return_example_decision_with_feedback()
        response = self.load_decision_list_page_and_return_response()
        decisions_table = response.context['decisions']
        self.assertTrue(isinstance(decisions_table, django_tables.ModelTable))
    
    def test_status_appears_in_table(self):
        self.create_and_return_example_decision_with_feedback()
        response = self.load_decision_list_page_and_return_response()
            
        self.check_cell_text_appears_in_table(response, "Proposal")

    def test_decision_list_can_be_filtered_by_status_proposal(self):
        self.create_decisions_with_different_statuses()
        params = {'status': Decision.PROPOSAL_STATUS }
        response = self.load_decision_list_page_and_return_response(data=params)
        self.check_cell_text_appears_in_table(response, "Proposal Decision")
        self.check_cell_text_does_not_appear_in_table(response, "Consensus Decision")
        self.check_cell_text_does_not_appear_in_table(response, "Archived Decision")
    
    def test_decision_list_can_be_filtered_by_status_consensus(self):
        self.create_decisions_with_different_statuses()
        params = {'status':Decision.CONSENSUS_STATUS}
        response = self.load_decision_list_page_and_return_response(data=params)
        self.check_cell_text_appears_in_table(response, "Consensus Decision")
        self.check_cell_text_does_not_appear_in_table(response, "Proposal Decision")
        self.check_cell_text_does_not_appear_in_table(response, "Archived Decision")
    
    def test_decision_list_can_be_filtered_by_status_archived(self):
        self.create_decisions_with_different_statuses()
        params = {'status':Decision.ARCHIVED_STATUS}
        response = self.load_decision_list_page_and_return_response(data=params)
        self.check_cell_text_appears_in_table(response, "Archived Decision")
        self.check_cell_text_does_not_appear_in_table(response, "Consensus Decision")
        self.check_cell_text_does_not_appear_in_table(response, "Proposal Decision")
    
    
    def check_cell_text_appears_in_table(self, response, expected_text):
        row_text = self.get_table_cell_rows(response)
        failure_message = "%s unexpectedly missing from %s" % (expected_text,
                                                               row_text)        
        self.assertTrue(expected_text in row_text, msg=failure_message)
        
    def check_cell_text_does_not_appear_in_table(self, response, expected_text):
        row_text = self.get_table_cell_rows(response)
        failure_message = "%s unexpectedly found in %s" % (expected_text,
                                                           row_text)
        self.assertFalse(expected_text in row_text, msg=failure_message)
    
    def get_table_cell_rows(self, response):
        root = fromstring(response.content)        
        sel = CSSSelector('td, td a')
    
        row_text = []
    
        for element in sel(root):
            if str(element.text) != 'None':
                row_text.append(element.text)

        return row_text


    def test_header_class_is_sorted_straight_when_column_is_ordered(self):
        params = {'sort' : 'short_name'}
        response = self.load_decision_list_page_and_return_response(data=params)
    
        classes = self.get_table_header_classes(response)    
        self.assertEquals("sorted straight", classes[1])
    
    def test_header_class_is_sorted_reverse_when_column_is_reverse_ordered(self):
        params = {'sort' : '-short_name'}
        response = self.load_decision_list_page_and_return_response(data=params)
    
        classes = self.get_table_header_classes(response)    
        self.assertEquals("sorted reverse", classes[1])

    def test_header_has_no_class_when_column_is_not_ordered(self):
        response = self.load_decision_list_page_and_return_response()
        classes = self.get_table_header_classes(response)
        self.assertEquals(None, classes[0])

    def test_header_ids_are_internal_column_names(self):
        response = self.load_decision_list_page_and_return_response()
        ids = self.get_table_header_ids(response)
        self.assertEquals(['id', 'short_name', 'status_text', \
                           'unresolvedfeedback', 'decided_date', \
                           'review_date', 'expiry_date'], ids)
        
    def get_table_header_ids(self, response):
        return self.get_table_header_properties(response, 'id')

    def get_table_header_classes(self, response):
        return self.get_table_header_properties(response, 'class')
    
    def get_table_header_properties(self, response, name):
        root = fromstring(response.content)        
        sel = CSSSelector('th')
    
        properties = []
    
        for element in sel(root):
            properties.append(element.attrib.get(name, None))

        return properties
            
    def load_decision_list_page_and_return_response(self, data=None):
        if data is None:
            data = {}
        return self.client.get(reverse('decision_list'), data)
