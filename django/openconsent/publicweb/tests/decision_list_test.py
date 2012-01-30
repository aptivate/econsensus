from decision_test_case import DecisionTestCase
from publicweb.models import Decision
import datetime
from django.core.urlresolvers import reverse

class DecisionListTest(DecisionTestCase):

    def test_decisions_can_be_sorted_by_id(self):
        id_list = []
        for i in range(5, 0, -1):
            decision = Decision(description='Decision %d' % i)
            decision.save(self.user)
            id_list.append(decision.id)
            
        response = self.client.get(reverse('publicweb_item_list', args=['proposal']), {'sort':'id'})
                
        object_list = response.context['object_list']    
                
        for i in range(1, 6):
            self.assertEquals(id_list[i-1], object_list[i-1].id)
        
    def test_decisions_can_be_sorted_by_description(self):
        
        id_list = []        
        for i in range(5, 0, -1):
            decision = Decision(description='Decision %d' % i)
            decision.save(self.user)
            id_list.append(decision.id)
            
        response = self.client.get(reverse('publicweb_item_list', args=['proposal']), {'sort':'description'})
                
        object_list = response.context['object_list']    

        
        for i in range(1, 6):            
            self.assertEquals('Decision %d' % i, object_list[i-1].description)

    def test_decisions_can_be_sorted_by_deadline(self):
        self.assert_decisions_sorted_by_date_column('deadline')

    def test_decision_list_can_be_filtered_by_status(self):
        self.create_decisions_with_different_statuses()
        response = self.client.get(reverse('publicweb_item_list', args=['decision']))
        self.assertContains(response, "Issue Decision")
        self.assertNotContains(response, "Issue Proposal")
        self.assertNotContains(response, "Issue Archived") 
    
    def assert_decisions_sorted_by_date_column(self, column):
        # Create test decisions in reverse date order.         
        for i in range(5, 0, -1):
            decision = Decision(description='Decision %d' % i, 
                                status=Decision.DECISION_STATUS)
            setattr(decision, column, datetime.date(2001, 3, i))
            decision.save(self.user)
            
        response = self.client.get(reverse('publicweb_item_list', args=['decision']), dict(sort=column))
        
        object_list = response.context['object_list']    
                
        for i in range(1, 6):
            self.assertEquals(datetime.date(2001, 3, i), getattr(object_list[i-1], column))

