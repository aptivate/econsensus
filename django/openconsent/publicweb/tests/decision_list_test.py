from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

import datetime

from decision_test_case import DecisionTestCase
from publicweb.models import Decision, Feedback

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

    def test_list_pages_can_be_sorted_by_date(self):
        self.assert_list_page_sorted_by_date_column('decided_date')
        self.assert_list_page_sorted_by_date_column('effective_date')
        self.assert_list_page_sorted_by_date_column('review_date')
        self.assert_list_page_sorted_by_date_column('expiry_date')
        self.assert_list_page_sorted_by_date_column('deadline')
        self.assert_list_page_sorted_by_date_column('archived_date')

    def test_list_page_sorted_by_description(self):
        # Create test decisions in reverse date order.         
        decision = Decision(description="Apple",
                            status=Decision.DECISION_STATUS)
        decision.save(self.user)
        decision = Decision(description="Dandelion",
                            status=Decision.DECISION_STATUS)
        decision.save(self.user)
        decision = Decision(description="Blackberry",
                            status=Decision.DECISION_STATUS)
        decision.save(self.user)
        decision = Decision(description="Coconut",
                            status=Decision.DECISION_STATUS)
        decision.save(self.user)

        response = self.client.get(reverse('publicweb_item_list', args=['decision']), dict(sort='description'))
        
        object_list = response.context['object_list']
                        
        self.assertEquals("Apple", getattr(object_list[0], 'description'))
        self.assertEquals("Blackberry", getattr(object_list[1], 'description'))
        self.assertEquals("Coconut", getattr(object_list[2], 'description'))
        self.assertEquals("Dandelion", getattr(object_list[3], 'description'))


    def test_list_page_sorted_by_feedback(self):
        # Create test decisions in reverse date order.         
        decision1 = Decision(description="Apple",
                            status=Decision.DECISION_STATUS)
        decision1.save(self.user)
        feedback = Feedback(description="One", decision=decision1)
        feedback.save()
        feedback = Feedback(description="Two", decision=decision1)
        feedback.save()
        feedback = Feedback(description="Three", decision=decision1)
        feedback.save()

        decision2 = Decision(description="Coconut",
                            status=Decision.DECISION_STATUS)
        decision2.save()

        decision3 = Decision(description="Blackberry",
                            status=Decision.DECISION_STATUS)
        decision3.save(self.user)
        feedback = Feedback(description="One", decision=decision3)
        feedback.save()
        feedback = Feedback(description="Two", decision=decision3)
        feedback.save()

        response = self.client.get(reverse('publicweb_item_list', args=['decision']), dict(sort='feedback'))
        
        object_list = response.context['object_list']
                        
        self.assertEquals(decision1.id, getattr(object_list[0], 'id'))
        self.assertEquals(decision3.id, getattr(object_list[1], 'id'))
        self.assertEquals(decision2.id, getattr(object_list[2], 'id')) 

    def test_list_page_sorted_by_watchers(self):
        adam = User.objects.get(username='Adam')
        barry = User.objects.get(username='Barry')
        charlie = User.objects.get(username='Charlie')
        
        decision1 = Decision(description="Apple",
                            status=Decision.DECISION_STATUS)
        decision1.save(self.user)
        decision1.watchers.add(barry)
        decision1.watchers.add(charlie)

        decision2 = Decision(description="Coconut",
                            status=Decision.DECISION_STATUS)
        decision2.save()

        decision3 = Decision(description="Blackberry",
                            status=Decision.DECISION_STATUS)
        decision3.save(self.user)
        decision3.watchers.add(barry)
        
        response = self.client.get(reverse('publicweb_item_list', args=['decision']), dict(sort='watchers'))

        object_list = response.context['object_list']
                        
        self.assertEquals(decision1.id, getattr(object_list[0], 'id'))
        self.assertEquals(decision3.id, getattr(object_list[1], 'id'))
        self.assertEquals(decision2.id, getattr(object_list[2], 'id')) 


    def test_decision_list_can_be_filtered_by_status(self):
        self.create_decisions_with_different_statuses()
        response = self.client.get(reverse('publicweb_item_list', args=['decision']))
        self.assertContains(response, "Issue Decision")
        self.assertNotContains(response, "Issue Proposal")
        self.assertNotContains(response, "Issue Archived") 
    
    def assert_list_page_sorted_by_date_column(self, column):
        # Create test decisions in reverse date order.         
        decision = Decision(description="Decision None 1",
                            status=Decision.DECISION_STATUS)
        decision.save(self.user)
        
        for i in range(5, 0, -1):
            decision = Decision(description='Decision %d' % i, 
                                status=Decision.DECISION_STATUS)
            setattr(decision, column, datetime.date(2001, 3, i))
            decision.save(self.user)
        
        decision = Decision(description="Decision None 2",
                            status=Decision.DECISION_STATUS)
        decision.save(self.user)

        #note that we don't actually have to _display_ the field to sort bny it
        response = self.client.get(reverse('publicweb_item_list', args=['decision']), dict(sort=column))
        
        object_list = response.context['object_list']
                
        for i in range(1, 6):
            self.assertEquals(datetime.date(2001, 3, i), getattr(object_list[i-1], column))

        self.assertEquals(None, getattr(object_list[5], column))
        self.assertEquals(None, getattr(object_list[6], column))
        
        Decision.objects.all().delete()