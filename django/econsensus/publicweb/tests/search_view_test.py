from django.test import TestCase
from django.test.client import RequestFactory
from django.template import RequestContext

from haystack.query import EmptySearchQuerySet

from publicweb.views import DecisionSearchView
from publicweb.models import Decision

from publicweb.tests.factories import DecisionFactory, OrganizationFactory, UserFactory
import  minimock

class MockSearchQuerySet(object):
    """
    Implementation of a minimal subset of the Haystack SearchQuerySet API.
    Does not require a search backend. Wraps a regular Django QuerySet.
    """
    def __init__(self, query_set):
        self.query_set = query_set

    def filter(self, **kargs):
        return MockSearchQuerySet.make(self.query_set.filter(**kargs))

    def __getitem__(self, index):
        return self.query_set[index]

    def __len__(self):
        return len(self.query_set)

    @classmethod
    def make(cls, query_set):
        if query_set:
            return cls(query_set)
        else:
            return EmptySearchQuerySet()

class TestDecisionSearchView(TestCase):
    def setUp(self):
        """
        Nadgers haystack SearchView so that:
        - we don't need a search backend
        - response is a TemplateResponse, not and HttpResponse (so
          that in tests we can check context contents)
        """
        import django.template.response
        import haystack.views
        
        # SearchView passes a RequestContext to render_to_response,
        # but we want to be able to get hold of the request itself
        # (to pass on to TemplateResponse).
        class RequestContext(django.template.response.RequestContext):
            def __init__(self, request):
                super(RequestContext, self).__init__(request)
                self.request = request

        def render_to_response(template, context, context_instance):
            return django.template.response.TemplateResponse(
                    request = context_instance.request,
                    template = template,
                    context = context)

        self.context_class = RequestContext
        minimock.mock("haystack.views.render_to_response", returns_func=render_to_response, tracker=None)
        minimock.mock("haystack.views.SearchView.get_results", returns_func=self.get_results, tracker=None)

        self.org = OrganizationFactory()

    def tearDown(self):
        minimock.restore()

    def get_results(self):
        """
        To avoid the need for a search backend, we just say that
        every decision matches every text search term.
        """
        return MockSearchQuerySet.make(Decision.objects.all())

    def do_search_request(self, **params):
        kwargs = {'org_slug': self.org.slug}
        request = RequestFactory().get('/', params)
        request.user = UserFactory.build()
        request.session = {}
        view = DecisionSearchView()
        view.context_class = self.context_class
        return view(request, **kwargs)

    def test_no_search(self):
        """
        Test content of search page context for when no search is
        being done (e.g. when user has just clicked on search tab).
        """

        response = self.do_search_request()
        context = response.context_data

        self.assertEqual(context.get('tab'), 'search')
        self.assertFalse(context.get('query'))
        self.assertEqual(self.org, context.get('organization'))
        self.assertFalse(context.get('page'))

    def test_no_results(self):
        """
        Test content of search page context for when a search
        yields no results.
        """
        response = self.do_search_request(q='aardvark')
        context = response.context_data

        self.assertEqual(context.get('tab'), 'search')
        self.assertEqual('aardvark', context.get('query'))
        self.assertEqual(self.org, context.get('organization'))
        self.assertFalse(context.get('page'))

    def test_one_result(self):
        """
        Test content of search page context for when a search
        yields a single result.
        """
        decision = DecisionFactory(organization=self.org)

        response = self.do_search_request(q='aardvark')
        context = response.context_data

        self.assertEqual(context.get('tab'), 'search')
        self.assertEqual('aardvark', context.get('query'))
        self.assertEqual(self.org, context.get('organization'))
        self.assertTrue(context.get('page'))
        page = context.get('page')
        self.assertEqual(1, len(page.object_list))
        self.assertFalse(page.has_previous())
        self.assertFalse(page.has_next())
        self.assertEquals(1, page.number)
        self.assertEquals(1, page.paginator.num_pages)

    def test_one_result_in_correct_org(self):
        """
        Test content of search page context for when a search
        yields a single result, but only because all but one
        of the matching decisions are in an organization that
        we are not looking in.
        """
        decision = DecisionFactory(organization=self.org)
        other_org = OrganizationFactory()
        for _ in range(100):
            other_decision = DecisionFactory(organization=other_org)

        response = self.do_search_request(q='aardvark')
        context = response.context_data

        self.assertEqual(context.get('tab'), 'search')
        self.assertEqual('aardvark', context.get('query'))
        self.assertEqual(self.org, context.get('organization'))
        self.assertTrue(context.get('page'))
        page = context.get('page')
        self.assertEqual(1, len(page.object_list))
        self.assertFalse(page.has_previous())
        self.assertFalse(page.has_next())
        self.assertEquals(1, page.number)
        self.assertEquals(1, page.paginator.num_pages)

    def test_more_than_one_page(self):
        """
        Test content of search page context for when a search
        yields results that must be split across two pages.
        """
        for _ in range(20):
            decision = DecisionFactory(organization=self.org)

        response = self.do_search_request(q='aardvark')
        context = response.context_data

        self.assertEqual(context.get('tab'), 'search')
        self.assertEqual('10', context.get('num'))
        self.assertEqual('aardvark', context.get('query'))
        self.assertEqual(self.org, context.get('organization'))
        page = context.get('page')
        self.assertEqual(10, len(page.object_list))
        self.assertFalse(page.has_previous())
        self.assertTrue(page.has_next())
        self.assertEquals(1, page.number)
        self.assertEquals(2, page.paginator.num_pages)
        self.assertEquals("?q=aardvark", context.get("queryurl"))

    def test_middle_page_with_nondefault_items_per_page(self):
        """
        Test content of search page context for when a search
        yields results that must be split across three pages.
        To make things more interesting, we are not using
        the default number of items per page, and we are asking
        for the second of the pages.
        """
        for _ in range(75):
            decision = DecisionFactory(organization=self.org)

        response = self.do_search_request(q='aardvark', num='25', page='2')
        context = response.context_data

        self.assertEqual(context.get('tab'), 'search')
        self.assertEqual('25', context.get('num'))
        self.assertEqual('aardvark', context.get('query'))
        self.assertEqual(self.org, context.get('organization'))
        page = context.get('page')
        self.assertEqual(25, len(page.object_list))
        self.assertTrue(page.has_previous())
        self.assertTrue(page.has_next())
        self.assertEquals(2, page.number)
        self.assertEquals(3, page.paginator.num_pages)
        self.assertEquals("?q=aardvark&num=25", context.get("queryurl"))
