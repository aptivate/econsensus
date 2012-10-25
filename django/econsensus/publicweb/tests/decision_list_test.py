from django.core.urlresolvers import reverse

import datetime

from decision_test_case import DecisionTestCase
from publicweb.models import Decision, Feedback
from lxml.html.soupparser import fromstring
from lxml.cssselect import CSSSelector


class DecisionListTest(DecisionTestCase):

    def test_decisions_can_be_sorted_by_id(self):
        db_list = [x.id for x in Decision.objects.filter(organization=self.bettysorg, status='proposal').order_by('id')]
        response = self.client.get(reverse('publicweb_item_list', args=[self.bettysorg.slug, 'proposal']), {'sort': 'id'})
        site_list = [x.id for x in response.context['object_list']]
        self.assertEquals(db_list, site_list)

    def test_decisions_can_be_sorted_by_description(self):
        db_list = [x.description for x in Decision.objects.filter(organization=self.bettysorg, status='proposal').order_by('description')]
        response = self.client.get(reverse('publicweb_item_list', args=[self.bettysorg.slug, 'proposal']), {'sort': 'description'})
        site_list = [x.description for x in response.context['object_list']]
        self.assertEquals(db_list, site_list)

    def test_all_sorts_result_in_one_arrow_present(self):
        """Assert only one sort class is present in the decision list view"""
        # Assumes CSS will be correctly displaying the sort status
        # Takes into account sort and sort-reverse
        sort_options = {'proposal': ['-id', 'excerpt', 'feedback', 'deadline', '-last_modified'],
                        'decision': ['-id', 'excerpt', 'decided_date', 'review_date'],
                        'archived': ['-id', 'excerpt', 'creation', 'archived_date']
                        }
        self.create_decisions_with_different_statuses()
        for page, sort_queries in sort_options.iteritems():
            for sort_query in sort_queries:
                response = self.client.get(reverse('publicweb_item_list', args=[self.bettysorg.slug, page]), {'sort': sort_query})
                html = fromstring(response.content)
                sort_selector = CSSSelector('table.summary-list .sort')
                sorts = sort_selector(html)
                self.assertEquals(len(sorts), 1, 'Number of sort arrows should be 1. But is ' + str(len(sorts))
                                                 + ' for page=' + page + ' sort_query=' + sort_query)

    def test_list_pages_can_be_sorted_by_date(self):
        self.assert_list_page_sorted_by_date_column('decided_date')
        self.assert_list_page_sorted_by_date_column('effective_date')
        self.assert_list_page_sorted_by_date_column('review_date')
        self.assert_list_page_sorted_by_date_column('expiry_date')
        self.assert_list_page_sorted_by_date_column('deadline')
        self.assert_list_page_sorted_by_date_column('archived_date')

    def test_list_page_sorted_by_description(self):
        # Create test decisions in reverse date order.
        self.make_decision(description="Apple", organization=self.bettysorg)
        self.make_decision(description="Dandelion", organization=self.bettysorg)
        self.make_decision(description="Blackberry", organization=self.bettysorg)
        self.make_decision(description="Coconut", organization=self.bettysorg)

        response = self.client.get(reverse('publicweb_item_list', args=[self.bettysorg.slug, 'proposal']), dict(sort='description'))

        object_list = response.context['object_list']

        self.assertEquals("Apple", getattr(object_list[0], 'description'))
        self.assertEquals("Blackberry", getattr(object_list[1], 'description'))
        self.assertEquals("Coconut", getattr(object_list[2], 'description'))
        self.assertEquals("Dandelion", getattr(object_list[3], 'description'))

    def test_list_page_sorted_by_feedback(self):
        # Create test decisions in reverse date order.
        Decision.objects.all().delete()
        decision1 = self.make_decision(description="Apple", organization=self.bettysorg)
        decision2 = self.make_decision(description="Coconut", organization=self.bettysorg)
        decision3 = self.make_decision(description="Blackberry", organization=self.bettysorg)
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
        self.make_decision(description="Decision None 1", organization=self.bettysorg)

        for i in range(5, 0, -1):
            decision = self.make_decision(description='Decision %d' % i, organization=self.bettysorg)
            setattr(decision, column, datetime.date(2001, 3, i))
            decision.save()

        self.make_decision(description="Decision None 2", organization=self.bettysorg)

        #note that we don't actually have to _display_ the field to sort by it
        response = self.client.get(reverse('publicweb_item_list', args=[self.bettysorg.slug, 'proposal']), dict(sort=column))

        object_list = response.context['object_list']

        for i in range(1, 6):
            self.assertEquals(datetime.date(2001, 3, i), getattr(object_list[i - 1], column))

        self.assertEquals(None, getattr(object_list[5], column))
        self.assertEquals(None, getattr(object_list[6], column))
        Decision.objects.all().delete()
