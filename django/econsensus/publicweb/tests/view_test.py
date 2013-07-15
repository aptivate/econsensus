from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from guardian.shortcuts import assign

from publicweb.views import DecisionDetail, DecisionList, DecisionUpdate, \
    FeedbackCreate, OrganizationRedirectView, YourDetails
from publicweb.models import Decision
from publicweb.forms import DecisionForm, FeedbackForm, YourDetailsForm
from organizations.models import Organization

from publicweb.tests.econsensus_testcase import EconsensusTestCase
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
        self.assertIn('tab', context.keys())
        self.assertEqual(context['tab'], manual_status)


class TestYourDetailsView(TestCase):

    def setUp(self):
        self.user = UserFactory(
            username = 'bob',
            email = 'bob@example.com',
            first_name = 'Bob',
            last_name = 'Dylan',
            is_staff = True)
        self.request = RequestFactory().get('blah')
        self.request.user = self.user
        self.view = YourDetails()

    def test_get_object(self):
        self.view.request = self.request
        self.assertEqual(self.view.get_object(), self.user)

    def test_form_contains_correct_fields(self):
        self.view.request = self.request
        self.view.object = self.user
        self.form = self.view.get_form(self.view.get_form_class())
        self.assertEqual(
            sorted(self.form.fields.keys()),
            sorted(['username', 'email', 'first_name', 'last_name']))

    def test_change_first_name(self):
        self.request.method = 'POST'
        self.view.request = self.request
        self.view.object = self.user
        # RequestFactory doesn't support middleware eg. message middleware
        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)
        self.view.request.POST = {
            'username': self.user.username,
            'email': self.user.email,
            'first_name': 'Robert',
            'is_staff': False
        }
        self.form = self.view.get_form(self.view.get_form_class())
        self.assertTrue(self.form.is_valid(), msg="Form is not valid: %s" % self.form.errors)
        self.view.form_valid(self.form)
        self.assertEqual(self.user.first_name, 'Robert')
        self.assertEqual(self.user.username, 'bob')
        self.assertEqual(self.user.email, 'bob@example.com')
        self.assertEqual(self.user.last_name, '')
        self.assertEqual(self.user.is_staff, True)
        expected_messages = [_('Your details have been updated successfully.')]
        self.assertEqual([str(item) for item in self.request._messages], expected_messages)


class TestDecisionUpdateView(EconsensusTestCase):

    def test_user_can_unwatch_a_decision(self):
        org_user = OrganizationUserFactory()
        org = org_user.organization
        user = org_user.user
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
        decision_update_view.form_valid(form)
        self.assertEqual(decision.editor, user2)

    def test_decision_editor_set_on_update_via_admin(self):
        user = UserFactory(username='creator')
        decision = DecisionFactory(
            author = user, 
            editor = user,
            description = "Lorem Ipsum"
        )

        new_organization = OrganizationFactory()
        admin_user = self.login_admin_user()
        self.change_decision_via_admin(decision, new_organization)

        decision = Decision.objects.get(id=decision.id)
        self.assertEquals(decision.editor, admin_user)

    def test_decision_last_status_set_on_update(self):
        status = Decision.DECISION_STATUS
        user = UserFactory()
        decision = DecisionFactory(author = user,
                                   editor = user,
                                   description = 'Lorem',
                                   status = status)
        self.assertEquals(decision.last_status, 'new')

        request = RequestFactory().get('/')
        assign('edit_decisions_feedback', user, decision.organization)
        request.user = user
        request.method = 'POST'
        request.POST = {'status': decision.status, 'description': decision.description}
        kwargs = {'pk': decision.id}
        DecisionUpdate.as_view()(request, **kwargs)

        decision = Decision.objects.get(id=decision.id)
        self.assertEqual(decision.last_status, status)

    def test_decision_last_status_set_on_update_via_admin(self):
        status = Decision.DECISION_STATUS
        user = UserFactory()
        decision = DecisionFactory(
            author = user,
            editor = user,
            description = "Lorem",
            status = status)
        self.assertEquals(decision.last_status, 'new')
        self.login_admin_user()
        self.change_decision_via_admin(decision)
        decision = Decision.objects.get(id=decision.id)
        self.assertEqual(decision.last_status, status)


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
        feedback = decision.feedback_set.get()
        self.assertEqual(feedback.author, user)


class TestDecisionModel(TestCase):

    def test_active_users_of_org_added_to_watchers_of_new_decision(self):
        """
        See no reason to have this in a view test, this behavior is almost
        entirely tested already in the model tests in tests/decisions_test.py
        Suggest, moving this test to there.
        """
        org = OrganizationFactory()
        active_org_user1 = OrganizationUserFactory(
            organization=org)
        active_org_user2 = OrganizationUserFactory(
            organization=org)
        inactive_org_user = OrganizationUserFactory(
            user = UserFactory(is_active=False),
            organization = org)
        active_other_org_user = OrganizationUserFactory()
        
        decision = DecisionFactory(organization=org)
        watching_user_ids = decision.watchers.values_list('user_id', flat=True)
        self.assertIn(active_org_user1.user.id, watching_user_ids)
        self.assertIn(active_org_user2.user.id, watching_user_ids)
        self.assertEqual(len(watching_user_ids), 2)


class TestOrganizationRedirectView(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.login_request = RequestFactory()
        self.login_request.user = self.user

    def test_redirect_for_one_organization(self):
        '''
        If the user is a member of only one organization then on login
        they should be redirected to the default Decision status list for 
        that one organization and not the organization list page.
        '''
        org_user = OrganizationUserFactory(user=self.user)
        org_redirect_view = OrganizationRedirectView()
        org_redirect_view.request = self.login_request
        url = org_redirect_view.get_redirect_url()
        expected_url = reverse('publicweb_item_list',
                               args=[org_user.organization.slug,
                                     'discussion'])
        self.assertEqual(url, expected_url)

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
        url = org_redirect_view.get_redirect_url()
        self.assertEquals(url, reverse('organization_list'))
