from django.core.urlresolvers import reverse

from decision_test_case import DecisionTestCase
from publicweb.models import Decision
from publicweb.views import DecisionList


class DecisionListTest(DecisionTestCase):

    def tearDown(self):
        Decision.objects.all().delete()

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
                      {'name': 'Test D', 'sessionnum': 25, 'querydict': {'num': '-ee'}, 'expectednum': '10'},
                      {'name': 'Test E', 'sessionnum': 25, 'querydict': {'page': 1}, 'expectednum': '10'}]
        for test_case in test_cases:
                # Ensure session is clean by logging out and in again
                self.client.get(reverse('auth_logout'))
                self.login('betty')
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
