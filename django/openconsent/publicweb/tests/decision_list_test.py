from django.core.urlresolvers import reverse

import datetime

from decision_test_case import DecisionTestCase
from publicweb.models import Decision, Feedback

class DecisionListTest(DecisionTestCase):

    def test_decisions_can_be_sorted_by_id(self):
        db_list = [x.id for x in Decision.objects.filter(organization=self.bettysorg, status='proposal').order_by('id')]
        response = self.client.get(reverse('publicweb_item_list', args=[self.bettysorg.slug, 'proposal']), {'sort':'id'})
        site_list = [x.id for x in response.context['object_list']]    
        self.assertEquals(db_list, site_list)
        
    def test_decisions_can_be_sorted_by_description(self):
        db_list = [x.description for x in Decision.objects.filter(organization=self.bettysorg, status='proposal').order_by('description')]
        response = self.client.get(reverse('publicweb_item_list', args=[self.bettysorg.slug, 'proposal']), {'sort':'description'})
        site_list = [x.description for x in response.context['object_list']]    
        
        self.assertEquals(db_list, site_list)

    def test_list_pages_can_be_sorted_by_date(self):
        Decision.objects.all().delete()   
        self.assert_list_page_sorted_by_date_column('decided_date')
        self.assert_list_page_sorted_by_date_column('effective_date')
        self.assert_list_page_sorted_by_date_column('review_date')
        self.assert_list_page_sorted_by_date_column('expiry_date')
        self.assert_list_page_sorted_by_date_column('deadline')
        self.assert_list_page_sorted_by_date_column('archived_date')

    def test_list_page_sorted_by_description(self):
        # Create test decisions in reverse date order.
        Decision.objects.all().delete()
        self.make_decision(description="Apple")
        self.make_decision(description="Dandelion")
        self.make_decision(description="Blackberry")
        self.make_decision(description="Coconut")

        response = self.client.get(reverse('publicweb_item_list', args=[self.bettysorg.slug, 'proposal']), dict(sort='description'))
        
        object_list = response.context['object_list']
                        
        self.assertEquals("Apple", getattr(object_list[0], 'description'))
        self.assertEquals("Blackberry", getattr(object_list[1], 'description'))
        self.assertEquals("Coconut", getattr(object_list[2], 'description'))
        self.assertEquals("Dandelion", getattr(object_list[3], 'description'))


    def test_list_page_sorted_by_feedback(self):
        # Create test decisions in reverse date order.         
        Decision.objects.all().delete()  
        decision1 = self.make_decision(description="Apple")
        decision2 = self.make_decision(description="Coconut")
        decision3 = self.make_decision(description="Blackberry")
        Feedback(description="One", decision=decision1, author=self.user).save()
        Feedback(description="Two", decision=decision1, author=self.user).save()
        Feedback(description="Three", decision=decision1, author=self.user).save()
        Feedback(description="One", decision=decision3, author=self.user).save()
        Feedback(description="Two", decision=decision3, author=self.user).save()

        response = self.client.get(reverse('publicweb_item_list', args=[self.bettysorg.slug, 'proposal']), dict(sort='feedback'))
        
        object_list = response.context['object_list']
                        
        self.assertEquals(decision1.id, getattr(object_list[0], 'id'))
        self.assertEquals(decision3.id, getattr(object_list[1], 'id'))
        self.assertEquals(decision2.id, getattr(object_list[2], 'id')) 

    def test_decision_list_can_be_filtered_by_status(self):
        self.create_decisions_with_different_statuses()
        response = self.client.get(reverse('publicweb_item_list', args=[self.bettysorg.slug, 'decision']))
        self.assertContains(response, "Issue Decision")
        self.assertNotContains(response, "Issue Proposal")
        self.assertNotContains(response, "Issue Archived") 
        response = self.client.get(reverse('publicweb_item_list', args=[self.bettysorg.slug, 'proposal']))
        self.assertContains(response, "Last Modified") 
        
    def assert_list_page_sorted_by_date_column(self, column):
        # Create test decisions in reverse date order.         
        self.make_decision(description="Decision None 1")
        
        for i in range(5, 0, -1):
            decision = self.make_decision(description='Decision %d' % i)
            setattr(decision, column, datetime.date(2001, 3, i))
            decision.save()

        self.make_decision(description="Decision None 2")

        #note that we don't actually have to _display_ the field to sort by it
        response = self.client.get(reverse('publicweb_item_list', args=[self.bettysorg.slug, 'proposal']), dict(sort=column))
        
        object_list = response.context['object_list']
                
        for i in range(1, 6):
            self.assertEquals(datetime.date(2001, 3, i), getattr(object_list[i-1], column))

        self.assertEquals(None, getattr(object_list[5], column))
        self.assertEquals(None, getattr(object_list[6], column))
        
        Decision.objects.all().delete()