from django.core.urlresolvers import reverse

import datetime
import random

from decision_test_case import DecisionTestCase
from publicweb.models import Decision, Feedback
from publicweb.views import DecisionList
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
        Decision.objects.all().delete()
        # these are the dates we'll set in the test (also defines number of decisions that get made)
        random_dates = [datetime.date.fromordinal(random.randint(500000, 800000)) for i in range(3)]
        # set all the columns you want to test sorting on
        columns = ['decided_date', 'effective_date', 'review_date', 'expiry_date', 'deadline', 'archived_date']

        # make an initial empty decision
        self.make_decision(description="Decision None 1", organization=self.bettysorg)

        # create decisions with dates - add the same date to all the columns
        for random_date in random_dates:
            d = self.make_decision(description='Decision %s' % random_date, organization=self.bettysorg)
            for column in columns:
                setattr(d, column, random_date)
            d.save()

        # make a final empty decision
        self.make_decision(description="Decision None 2", organization=self.bettysorg)

        # we need sorted dates to compare the return values against
        sorted_dates_forward = sorted(random_dates)
        sorted_dates_reverse = sorted_dates_forward[::-1]

        for column in columns:
            response_forward = self.client.get(reverse('publicweb_item_list', args=[self.bettysorg.slug, 'proposal']), dict(sort=column))
            object_list_forward = response_forward.context['object_list']

            response_reverse = self.client.get(reverse('publicweb_item_list', args=[self.bettysorg.slug, 'proposal']), dict(sort='-' + column))
            object_list_reverse = response_reverse.context['object_list']

            object_list_length = len(object_list_forward)
            self.assertEquals(len(object_list_forward), len(object_list_reverse))

            #Test everything
            for index, sorted_date_forward in enumerate(sorted_dates_forward):
                self.assertEquals(sorted_date_forward, getattr(object_list_forward[index], column))
                self.assertEquals(sorted_dates_reverse[index], getattr(object_list_reverse[index], column))
            self.assertEquals(None, getattr(object_list_forward[object_list_length - 2], column))
            self.assertEquals(None, getattr(object_list_forward[object_list_length - 1], column))
            self.assertEquals(None, getattr(object_list_reverse[object_list_length - 2], column))
            self.assertEquals(None, getattr(object_list_reverse[object_list_length - 1], column))

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

    def test_pagination_set_paginate_by(self):
        # Test the following cases confirming both self.paginate_by and session['num'] is set
        # happy path:
        # A) if valid num in 'get' set it (and prefer it over session)
        # B) if nothing in get and something in session use session
        # C) if nothing in session or get use default
        # less happy path:
        # D) if invalid (ee or '-10') set default
        # E) if page number but no num set default (Note: this has to be a valid page so we have to use page=1 if we don't create lots of decisions)
        test_cases = [{'name': 'Test A', 'sessionnum': 25, 'querydict': {'num': 100}, 'expectednum': '100'},
                      {'name': 'Test B', 'sessionnum': 25, 'querydict': {'sort': '-id'}, 'expectednum': '25'},
                      {'name': 'Test C', 'sessionnum': None, 'querydict': {'sort': '-id'}, 'expectednum': '10'},
                      {'name': 'Test D', 'sessionnum': 25, 'querydict':  {'num': '-ee'}, 'expectednum': '10'},
                      {'name': 'Test E', 'sessionnum': 25, 'querydict':  {'page': 1}, 'expectednum': '10'}]
        for test_case in test_cases:
                # Ensure session is clean by logging out and in again
                self.client.get(reverse('auth_logout'))
                #self.login('betty') <-- TODO Don't seem to need to login??? (related to method_decorator being commented out?)
                self.assertFalse('num' in self.client.session, 'Session should be empty at start of test')

                # Set an existing session val if we need one
                if test_case['sessionnum']:
                    s = self.client.session
                    s['num'] = test_case['sessionnum']
                    s.save()
                response = self.client.get(reverse('publicweb_item_list', args=[self.bettysorg.slug, 'proposal']), test_case['querydict'])

                curr_session_num = str(self.client.session.get('num'))
                paginator_num = str(response.context['page_obj'].paginator.per_page)

                self.assertEquals(curr_session_num, test_case['expectednum'], "We did not get the expected session value for " + test_case['name'])
                self.assertEquals(paginator_num, test_case['expectednum'], "We did not get the expected paginator value for " + test_case['name'])

    def test_pagination_build_query_string(self):
        # Test the following cases confirm expected string is returned
        # A) all defaults - expect next and prev page numbers only
        # B) non-default sort - expect page numbers with sort
        # C) non-default num - expect page numbers with num
        # D) non-default sort and num - expect page numbers with num and sort
        # E) no page_obj - expect None
        # Run where prev_page = 2 & next_page = 4

        default_num = '10'
        default_sort = '-id'

        decision_list = DecisionList()
        decision_list.default_num_items = default_num

        # Set up a dummy page object
        class DummyPageObject:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)
        page_obj = DummyPageObject(previous_page_number=lambda: 2, next_page_number=lambda: 4)

        test_cases = [{'name': 'Test A', 'page_obj': page_obj, 'context': {'num': default_num, 'sort': default_sort}, 'expectedprev': '?page=2', 'expectednext': '?page=4'},
                      {'name': 'Test B', 'page_obj': page_obj, 'context': {'num': default_num, 'sort': 'excerpt'}, 'expectedprev': '?sort=excerpt&page=2', 'expectednext': '?sort=excerpt&page=4'},
                      {'name': 'Test C', 'page_obj': page_obj, 'context': {'num': '25', 'sort': default_sort}, 'expectedprev': '?num=25&page=2', 'expectednext': '?num=25&page=4'},
                      {'name': 'Test D', 'page_obj': page_obj, 'context': {'num': '25', 'sort': 'excerpt'}, 'expectedprev': '?sort=excerpt&num=25&page=2', 'expectednext': '?sort=excerpt&num=25&page=4'},
                      {'name': 'Test E', 'page_obj': None, 'context': {'num': '25', 'sort': 'feedback'}, 'expectedprev': None, 'expectednext': None}]

        for test_case in test_cases:
            context = test_case['context']
            context['page_obj'] = test_case['page_obj']
            returned_prev_string = decision_list.build_prev_query_string(context)
            returned_next_string = decision_list.build_next_query_string(context)
            self.assertEquals(returned_prev_string, test_case['expectedprev'], 'Did not get expected previous query')
            self.assertEquals(returned_next_string, test_case['expectednext'], 'Did not get expected next query')

    def _get_random_string(self, max_length_of_string):
        #TODO This does not generate non-english charaters
        chars = ascii_letters + digits + ' '
        return ''.join([chars[randint(0, len(chars) - 1)] for x in range(randint(1, max_length_of_string))])

    def _get_random_date(self):
        return date.fromordinal(randint(500000, 800000))

