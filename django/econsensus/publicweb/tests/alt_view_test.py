from django.test import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse

from publicweb.views import DecisionDetail, DecisionList, DecisionUpdate, \
    FeedbackCreate, OrganizationRedirectView
from publicweb.models import Decision
from publicweb.forms import DecisionForm, FeedbackForm
from organizations.models import Organization

from publicweb.tests.factories import DecisionFactory, OrganizationFactory, \
    OrganizationUserFactory, UserFactory


class TestDecisionListView(TestCase):

    def test_set_status_is_correctly_set_when_kwarg_is_passed(self):
        dl = DecisionList()
        kwargs = {'status': 'test status'}
        dl.set_status(**kwargs)
        self.assertEqual(dl.status, 'test status')

    def test_set_status_uses_default_when_no_kwarg_is_passed(self):
        dl = DecisionList()
        dl.set_status()
        default_status = Decision.PROPOSAL_STATUS
        self.assertEqual(dl.status, default_status)

    def test_status_is_set_in_context_data_and_limits_object_list(self):
        """
        More integrated test, that goes through dispatch, get, and
        get_context_data method to get the response object and test it.
        """
        decision = DecisionFactory(status=Decision.DECISION_STATUS)
        org = decision.organization
        archive = DecisionFactory(organization=org, status=Decision.ARCHIVED_STATUS)

        kwargs = {'org_slug': org.slug,
                  'status': archive.status}
        request = RequestFactory().get('/')
        request.user = UserFactory.build()
        request.session = {}
        response = DecisionList.as_view()(request, **kwargs)
        self.assertIn('tab', response.context_data.keys())
        self.assertEqual(response.context_data['tab'], archive.status)
        self.assertIn(archive, response.context_data['object_list'])
        self.assertNotIn(decision, response.context_data['object_list'])


class TestDecisionDetailView(TestCase):

    def test_status_is_set_in_decision_detail_context(self):
        """
        Same as test_status_is_set_in_decision_list_context but for
        decision_detail view.
        """
        dd = DecisionDetail()
        manual_status = 'i set the status'
        decision = Decision(status=manual_status, organization=Organization())
        dd.object = decision
        context = dd.get_context_data()
        self.assertEqual(context['tab'], manual_status)


class TestDecisionUpdateView(TestCase):

    def test_user_can_unwatch_a_decision(self):
        """
        There appears to be a duplicate test for the same
        in decisions_test.py
        """
        org_user_factory = OrganizationUserFactory()
        org = org_user_factory.organization
        user = org_user_factory.user
        decision = DecisionFactory(organization=org)
        # Confirm decision has a single watcher
        self.assertEqual(decision.watchers.count(), 1)
        # Get the view ready
        request = RequestFactory()
        request.user = user
        decision_update_view = DecisionUpdate()
        decision_update_view.request = request
        decision_update_view.object = decision
        decision_update_view.get_object = lambda: decision
        decision_update_view.last_status = 'dummy'
        form = DecisionForm(instance=decision)
        form.cleaned_data = {'watch': False}
        # Run the form_valid method to stop observing
        decision_update_view.form_valid(form)
        self.assertEqual(decision.watchers.count(), 0)

    def test_decision_editor_set_on_update(self):
        # Create the decision
        user1 = UserFactory()
        decision = DecisionFactory(author=user1,
                                   editor=user1)
        # Have a different user update it
        user2 = UserFactory()
        request = RequestFactory()
        request.user = user2
        decision_update_view = DecisionUpdate()
        decision_update_view.request = request
        decision_update_view.object = decision
        decision_update_view.get_object = lambda: decision
        decision_update_view.last_status = 'dummy'
        form = DecisionForm(instance=decision)
        form.cleaned_data = {'watch': True}
        # Run the form_valid method to stop observing
        decision_update_view.form_valid(form)
        self.assertEqual(decision.editor, user2)


class TestFeedbackCreateView(TestCase):

    def test_feedback_author_is_assigned_on_feedback_create(self):
        decision = DecisionFactory()
        user = UserFactory()
        request = RequestFactory()
        request.user = user
        feedback_create_view = FeedbackCreate()
        feedback_create_view.request = request
        feedback_create_view.kwargs = {'parent_pk': decision.id}
        form = FeedbackForm()
        form.cleaned_data = {}
        feedback_create_view.form_valid(form)
        feedback_author = decision.feedback_set.get().author
        self.assertEqual(feedback_author, user)


class TestDecisionModel(TestCase):

    def test_active_users_of_org_added_to_watchers_of_new_decision(self):
        """
        See no reason to have this in a view test, this behavior is almost
        entirely tested already in the model tests in tests/decisions_test.py
        Suggest, moving this test to there.
        """
        org_user_factory = OrganizationUserFactory()
        org = org_user_factory.organization
        user_in_org = org_user_factory.user
        UserFactory()  # Create one user not linked to the org for completeness
        user_inactive = UserFactory(is_active=False)
        # Link the inactive user with the existing org and confirm it worked
        OrganizationUserFactory(user=user_inactive, organization=org)
        user_status_list = [user.user.is_active
                            for user in org.organization_users.all()]
        assert user_status_list.count(True) == 1
        assert user_status_list.count(False) == 1
        # The Test
        decision = DecisionFactory(organization=org)
        self.assertEqual(decision.watchers.count(), 1,
                         "There should be one watcher.")
        self.assertEqual(decision.watchers.get().user, user_in_org,
                         "The watcher user should be the active user.")


class TestOrganizationRedirectView(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.login_request = RequestFactory()
        self.login_request.user = self.user

    def test_redirect_for_one_organization(self):
        '''
        If the user is a member of only one organization then on login
        they should be redirected to the proposal page for that one
        organization and not the organization list page.
        '''
        org_user_factory = OrganizationUserFactory(user=self.user)
        org_redirect_view = OrganizationRedirectView()
        org_redirect_view.request = self.login_request
        response = org_redirect_view.get_redirect_url()
        expected_url = reverse('publicweb_item_list',
                               args=[org_user_factory.organization.slug,
                                     'proposal'])
        self.assertEqual(response, expected_url)

    def test_redirect_for_many_organizations(self):
        '''
        If the user is a member of many organizations then on login
        they should be redirected to the organization list page
        which shows all the organizations to which they belong.
        '''
        OrganizationUserFactory(user=self.user)
        OrganizationUserFactory(user=self.user)
        org_redirect_view = OrganizationRedirectView()
        org_redirect_view.request = self.login_request
        response = org_redirect_view.get_redirect_url()
        self.assertEquals(response, reverse('organization_list'))
