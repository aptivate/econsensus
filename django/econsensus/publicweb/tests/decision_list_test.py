from django.core.urlresolvers import reverse

from random import randint, choice
from string import ascii_letters, digits
from datetime import date

from decision_test_case import DecisionTestCase
from publicweb.models import Decision, Feedback
from publicweb.views import DecisionList
from lxml.html.soupparser import fromstring
from lxml.cssselect import CSSSelector
from copy import deepcopy


class DecisionListTest(DecisionTestCase):

    def tearDown(self):
        Decision.objects.all().delete()

    def test_all_sorts_result_in_one_arrow_present(self):
        """Assert only one sort class is present in the decision list view"""

        # Assumes CSS will be correctly displaying the sort status
        decision_list = DecisionList()
        sort_options = deepcopy(decision_list.sort_table_headers)
        unsortable_headers = decision_list.unsortable_fields[:]

        for header_list in sort_options.values():
            for header in unsortable_headers:
                index = header_list.index(header)
                header_list.pop(index)

        self.create_decisions_with_different_statuses()

        # Test Ascending Sort
        for page, sort_queries in sort_options.iteritems():
            for sort_query in sort_queries:
                response = self.client.get(reverse('publicweb_item_list', args=[self.bettysorg.slug, page]), {'sort': sort_query})
                html = fromstring(response.content)
                sort_selector = CSSSelector('table.summary-list .sort-asc')
                sorts = sort_selector(html)
                self.assertEquals(len(sorts), 1, 'Number of ascending sort arrows should be 1. But is ' + str(len(sorts))
                                                 + ' for page=' + page + ' sort_query=' + sort_query)
        # Test Descending Sort
        for page, sort_queries in sort_options.iteritems():
            for sort_query in sort_queries:
                response = self.client.get(reverse('publicweb_item_list', args=[self.bettysorg.slug, page]), {'sort': '-' + sort_query})
                html = fromstring(response.content)
                sort_selector = CSSSelector('table.summary-list .sort-desc')
                sorts = sort_selector(html)
                self.assertEquals(len(sorts), 1, 'Number of descending sort arrows should be 1. But is ' + str(len(sorts))
                                                 + ' for page=' + page + ' sort_query=' + sort_query)

    def test_list_pages_can_be_sorted(self):
        """Test that sort works for all Decision List columns we offer it on"""
        number_of_test_decisions = 3  # Two additional empty decisions will be made

        # these are the dates we'll set in the test
        random_dates = [self._get_random_date() for i in range(number_of_test_decisions)]
        random_descriptions = [self._get_random_string(30) for i in range(number_of_test_decisions)]

        # set all the columns you want to test sorting on
        date_columns = ['deadline', 'decided_date', 'review_date', 'archived_date']

        #############################
        # Make the decisions
        #############################
        # Make an initial empty decision
        decisions = []
        decisions.append(self.make_decision(description="Decision None 1", organization=self.bettysorg))

        # Create decisions with random data
        for i in range(number_of_test_decisions):
            d = self.make_decision(description=random_descriptions[i], organization=self.bettysorg)
            for column in date_columns:
                setattr(d, column, random_dates[i])
            d.save()
            decisions.append(d)

        # Set random feedback (offset by 1 so empty decision remains empty)
        for i in range(1, number_of_test_decisions + 1):
            for f in range(randint(1, 4)):
                Feedback(description=self._get_random_string(10), decision=decisions[i], author=self.user).save()

        # Make a final empty decision
        decisions.append(self.make_decision(description="Decision None 2", organization=self.bettysorg))

        # Get the last_modified & id values
        last_modifieds = [decision.last_modified for decision in decisions]
        ids = [decision.id for decision in decisions]
        feedbackcounts = [decision.feedbackcount() for decision in decisions]
        excerpts = [decision.excerpt for decision in decisions]
        #############################

        # we need sorted values to compare against
        sorted_dates = sorted(random_dates)
        sorted_last_modifieds = sorted(last_modifieds)
        sorted_ids = sorted(ids)
        sorted_feedbackcounts = sorted(feedbackcounts)
        sorted_excerpts = sorted(excerpts, key=unicode.lower)

        # Test Dates
        for column in date_columns:
            response = self.client.get(reverse('publicweb_item_list', args=[self.bettysorg.slug, 'proposal']), dict(sort=column))
            object_list = response.context['object_list']

            for index, sorted_date in enumerate(sorted_dates):
                self.assertEquals(sorted_date, getattr(object_list[index], column), 'Testing date sort failed for' + column)
            self.assertEquals(None, getattr(object_list[len(object_list) - 2], column), 'Testing date sort failed for' + column)
            self.assertEquals(None, getattr(object_list[len(object_list) - 1], column), 'Testing date sort failed for' + column)

        # Test Last Modified
        response = self.client.get(reverse('publicweb_item_list', args=[self.bettysorg.slug, 'proposal']), {'sort': 'last_modified'})
        object_list = response.context['object_list']
        for index, sorted_last_modified in enumerate(sorted_last_modifieds):
            # Replace Microsecond to enable good results on MySQL and SQLLite
            sorted_list_last_modified = sorted_last_modified.replace(microsecond=0)
            object_list_last_modified = getattr(object_list[index], 'last_modified').replace(microsecond=0)
            self.assertEquals(sorted_list_last_modified, object_list_last_modified, 'Testing date sort failed for last_modified')

        # At this point, the ids in browser are all out of order, so good time to test id sort
        response = self.client.get(reverse('publicweb_item_list', args=[self.bettysorg.slug, 'proposal']), {'sort': 'id'})
        object_list = response.context['object_list']
        for index, sorted_id in enumerate(sorted_ids):
            self.assertEquals(sorted_id, getattr(object_list[index], 'id'), 'Testing id sort failed')

        # Test Feedback
        response = self.client.get(reverse('publicweb_item_list', args=[self.bettysorg.slug, 'proposal']), {'sort': 'feedback'})
        object_list = response.context['object_list']
        for index, sorted_feedbackcount in enumerate(sorted_feedbackcounts):
            self.assertEquals(sorted_feedbackcount, object_list[index].feedbackcount(), 'Testing feedbackcount sort failed.')

        # Test Excerpt
        response = self.client.get(reverse('publicweb_item_list', args=[self.bettysorg.slug, 'proposal']), {'sort': 'excerpt'})
        object_list = response.context['object_list']
        for index, sorted_excerpt in enumerate(sorted_excerpts):
            self.assertEquals(sorted_excerpt, getattr(object_list[index], 'excerpt'), 'Testing excerpt sort failed')

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

    def test_set_sorting(self):
        # Test the following cases confirm expected string is returned
        # A) None -> -id
        # B) random -> -id
        # C) valid sort option asc -> valid sort option
        # D) valid sort option desc -> - valid sort option

        valid_sort_options = DecisionList().sort_options.keys()

        test_c = choice(valid_sort_options)
        test_d = '-' + choice(valid_sort_options)

        test_cases = [{'name': 'Test A', 'sortquery': '-id', 'expectedsort': '-id', 'expectedsort_order': '-', 'expectedsort_field': 'id'},
                      {'name': 'Test B', 'sortquery': self._get_random_string(10), 'expectedsort': '-id', 'expectedsort_order': '-', 'expectedsort_field': 'id'},
                      {'name': 'Test C', 'sortquery': test_c, 'expectedsort': test_c, 'expectedsort_order': '', 'expectedsort_field': test_c},
                      {'name': 'Test D', 'sortquery': test_d, 'expectedsort': test_d, 'expectedsort_order': '-', 'expectedsort_field': test_d[1:]}]
        for test_case in test_cases:
            response = self.client.get(reverse('publicweb_item_list', args=[self.bettysorg.slug, 'proposal']), {'sort': test_case['sortquery']})
            self.assertEquals(response.context['sort'], test_case['expectedsort'], 'Did not get expected sort with sortquery ' + test_case['sortquery'])

    def test_sorting_header_links(self):
        # Ensure that the links provided in table headers give the correct next sort link
        # Use default sort for each sort_option and assert that other headers are correct.
        self.create_decisions_with_different_statuses()

        decision = DecisionList()
        default_sort_options = deepcopy(decision.sort_options)
        sort_table_headers = deepcopy(decision.sort_table_headers)
        unsortable_headers = decision.unsortable_fields[:]

        for header_list in sort_table_headers.values():
            for header in unsortable_headers:
                index = header_list.index(header)
                header_list.pop(index)

        for page, sort_queries in sort_table_headers.iteritems():
            page_url = reverse('publicweb_item_list', args=[self.bettysorg.slug, page])

            sort_query_defaults = {}
            # Build expected defaults
            for sort_query in sort_queries:
                default_sort_order = default_sort_options[sort_query]
                default_sort_query = default_sort_order + sort_query
                sort_query_defaults[sort_query] = default_sort_query
            sort_query_defaults['id'] = ''  # Override the default sort for id

            for sort_query in sort_queries:
                sort_query_tests = sort_query_defaults.copy()
                test_query = sort_query_tests.pop(sort_query)

                response = self.client.get(page_url, {'sort': test_query})
                html = fromstring(response.content)

                # Loop through the shortened sort_query_tests to check that default links are being given
                for selector, sort_query_test in sort_query_tests.iteritems():
                    selector = CSSSelector('.summary-header th.' + selector + ' a')
                    link_ending = selector(html)[0].attrib['href'].split(page_url)[1]

                    if sort_query_test == '':
                        self.assertFalse(link_ending)
                    else:
                        self.assertEquals(link_ending.split('?sort=')[1], sort_query_test)

                # Finally check that the test_query column has the opposite sort
                selector = CSSSelector('.summary-header th.' + sort_query + ' a')
                link_ending = selector(html)[0].attrib['href'].split(page_url)[1].split('?sort=')[1]
                reversed_sort_order = decision.toggle_sort_order(default_sort_options[sort_query])
                expected_link_ending = reversed_sort_order + sort_query
                self.assertEquals(expected_link_ending, link_ending)

    def test_toggle_sort_order(self):
        decision = DecisionList()
        self.assertEquals('', decision.toggle_sort_order('-'))
        self.assertEquals('-', decision.toggle_sort_order(''))

    def _get_random_string(self, max_length_of_string):
        # TODO This does not generate non-english charaters
        chars = ascii_letters + digits + ' '
        return ''.join([chars[randint(0, len(chars) - 1)] for x in range(randint(1, max_length_of_string))])

    def _get_random_date(self):
        return date.fromordinal(randint(500000, 800000))
