from publicweb.tests.decision_test_case import DecisionTestCase
from publicweb.models import Decision
import datetime
from django.core.urlresolvers import reverse
import django_tables2 as tables
from lxml.html import fromstring
from lxml.cssselect import CSSSelector

class ProposalListTest(DecisionTestCase):
    
    def test_only_proposals_are_returned(self):
        self.create_decisions_with_different_statuses()
        
        path = reverse('proposal_list')
        
        response = self.client.get(path)

        self.check_cell_text_appears_in_table(response, "Proposal Decision")
        self.check_cell_text_does_not_appear_in_table(response, "Consensus Decision")
        self.check_cell_text_does_not_appear_in_table(response, "Archived Decision")

    def test_proposals_table_rows_can_be_sorted_by_deadline(self):
        self.assert_proposals_table_sorted_by_date_column('deadline')

    def assert_proposals_table_sorted_by_date_column(self, column):
        # Create test decisions in reverse date order.         
        for i in range(5, 0, -1):
            proposal = Decision(description='Proposal %d' % i, 
                                status=Decision.PROPOSAL_STATUS)
            setattr(proposal, column, datetime.date(2001, 3, i))
            proposal.save(self.user)
            
        response = self.load_proposal_list_page_and_return_response(
            data=dict(sort=column))
        proposals_table = response.context['proposals']    
        
        # Check that decision rows are returned in normal order
        rows = list(proposals_table.rows)

        for i in range(1, 6):
            self.assertEquals(datetime.date(2001, 3, i), 
                              getattr(rows[i-1].record, column))

    def test_proposals_table_is_an_instance_of_model_table(self):
        """
        The decisions table is represented using django_tables2.ModelTable.
        """
        self.create_and_return_example_decision_with_feedback()
        response = self.load_proposal_list_page_and_return_response()
        proposals_table = response.context['proposals']
        self.assertTrue(isinstance(proposals_table, tables.Table))    
    
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
        sel = CSSSelector('.id a, .item_description p, .item_activity, .deadline span')
    
        row_text = []
    
        for element in sel(root):
            if str(element.text) != 'None':
                row_text.append(element.text)

        return row_text


    def test_header_class_is_sorted_straight_when_column_is_ordered(self):
        self.create_and_return_decision()
        params = {'sort' : 'description_excerpt'}
        response = self.load_proposal_list_page_and_return_response(data=params)
    
        classes = self.get_table_header_classes(response)    
        self.assertEquals("sorted straight", classes[1])
    
    def test_header_class_is_sorted_reverse_when_column_is_reverse_ordered(self):
        self.create_and_return_decision()
        params = {'sort' : '-description_excerpt'}
        response = self.load_proposal_list_page_and_return_response(data=params)
    
        classes = self.get_table_header_classes(response)    
        self.assertEquals("sorted reverse", classes[1])

    def test_header_has_no_class_when_column_is_not_ordered(self):
        self.create_and_return_decision()
        response = self.load_proposal_list_page_and_return_response()
        classes = self.get_table_header_classes(response)
        self.assertEquals(None, classes[0])

    def test_header_ids_are_internal_column_names(self):
        self.create_and_return_decision()
        response = self.load_proposal_list_page_and_return_response()
        ids = self.get_table_header_ids(response)
        self.assertEquals(['id', 'description_excerpt', \
                           'unresolvedfeedback', 'deadline'], ids)
        
    def get_table_header_ids(self, response):
        return self.get_table_header_properties(response, 'id')

    def get_table_header_classes(self, response):
        return self.get_table_header_properties(response, 'class')
    
    def get_table_header_properties(self, response, name):
        root = fromstring(response.content)        
        sel = CSSSelector('.headings span')
    
        properties = []
    
        for element in sel(root):
            properties.append(element.attrib.get(name, None))

        return properties
            
    def load_proposal_list_page_and_return_response(self, data=None):
        if data is None:
            data = {}
        return self.client.get(reverse('proposal_list'), data)
