from django.test import TestCase
from django.test.client import RequestFactory

from publicweb.tests.factories import OrganizationUserFactory, DecisionFactory,\
    ObservedItemFactory

from custom_organizations.views import CustomOrganizationCreate, \
    CustomOrganizationUpdate, CustomOrganizationUserUpdate, \
    CustomOrganizationUserCreate, CustomOrganizationUserDelete,\
    CustomOrganizationUserLeave
from custom_organizations.forms import CustomOrganizationAddForm, \
    CustomOrganizationForm, CustomOrganizationUserForm, \
    CustomOrganizationUserAddForm

from guardian.shortcuts import assign_perm
from notification.models import ObservedItem
from django.core.urlresolvers import reverse
from django.http import HttpResponseNotFound, Http404
GUARDIAN_PERMISSION = 'edit_decisions_feedback'


class TestCustomOrganizationCreate(TestCase):

    def test_form_class_is_CustomOrganizationAddForm(self):
        custom_org_create_view = CustomOrganizationCreate()
        self.assertIs(
            custom_org_create_view.get_form_class(),
            CustomOrganizationAddForm)


class TestCustomOrganizationUpdate(TestCase):

    def test_form_class_is_CustomOrganizationForm(self):
        custom_org_update_view = CustomOrganizationUpdate()
        self.assertIs(
            custom_org_update_view.get_form_class(),
            CustomOrganizationForm)


class TestCustomOrganizationUserUpdate(TestCase):

    def test_form_class_is_CustomOrganizationUserForm(self):
        custom_org_user_update_view = CustomOrganizationUserUpdate()
        self.assertIs(
            custom_org_user_update_view.get_form_class(),
            CustomOrganizationUserForm)

    def test_get_initial_returns_is_editor_status_and_nothing_else(self):
        custom_org_user_update_view = CustomOrganizationUserUpdate()
        # This will provide an organization and user, but no permissions will
        # be assigned so is_editor will be False
        custom_org_user_update_view.object = OrganizationUserFactory.build()
        expected_initial = {'is_editor': False}
        self.assertDictEqual(custom_org_user_update_view.get_initial(),
                             expected_initial)


class TestCustomOrganizationUserCreate(TestCase):

    def test_form_class_is_CustomOrganizationUserAddForm(self):
        custom_org_user_create_view = CustomOrganizationUserCreate()
        self.assertIs(
            custom_org_user_create_view.get_form_class(),
            CustomOrganizationUserAddForm)


class TestCustomOrganizationUserDelete(TestCase):

    def test_delete_deletes_the_unused_permissions(self):
        org_user_delete_view = CustomOrganizationUserDelete()
        org_user = OrganizationUserFactory()
        org = org_user.organization
        user = org_user.user
        assign_perm(GUARDIAN_PERMISSION, user, org)
        self.assertTrue(user.has_perm(GUARDIAN_PERMISSION, org))
        org_user_delete_view.get_object = lambda: org_user
        request = RequestFactory()
        request.user = user
        org_user_delete_view.delete(request)
        self.assertFalse(user.has_perm(GUARDIAN_PERMISSION, org))
    
    def test_delete_stops_users_watching_decisions_for_the_organization(self):
        org_user_delete_view = CustomOrganizationUserDelete()
        observed_item = ObservedItemFactory()
        org = observed_item.observed_object.organization
        user = observed_item.user
        org_user = OrganizationUserFactory(organization=org, user=user)
        decision = observed_item.observed_object
        org_user_delete_view.get_object = lambda: org_user
        request = RequestFactory()
        request.user = user
        org_user_delete_view.delete(request)
        self.assertSequenceEqual([], decision.watchers.all())

class TestCustomOrganizationUserLeave(TestCase):
    def test_organisation_user_leave_view_redirects_to_organization_list(self):
        org_user_leave_view = CustomOrganizationUserLeave()
        observed_item = ObservedItemFactory()
        org = observed_item.observed_object.organization
        user = observed_item.user
        org_user = OrganizationUserFactory(organization=org, user=user)
        org_user_leave_view.get_object = lambda: org_user
        request = RequestFactory()
        request.user = user
        response = org_user_leave_view.delete(request)
        self.assertEqual(reverse('organization_list'), response['Location'])
    
    def test_organisation_users_leave_view_is_only_accesible_by_user(self):
        org_user_leave_view = CustomOrganizationUserLeave()
        
        observed_item_1 = ObservedItemFactory()
        org_1 = observed_item_1.observed_object.organization
        user_1 = observed_item_1.user
        org_user = OrganizationUserFactory(organization=org_1, user=user_1)
        
        observed_item_2 = ObservedItemFactory()
        org_2 = observed_item_2.observed_object.organization
        user_2 = observed_item_2.user
        OrganizationUserFactory(organization=org_2, user=user_2)
        
        org_user_leave_view.get_object = lambda: org_user
        request = RequestFactory()
        request.user = user_2

        self.assertRaises(Http404, org_user_leave_view.dispatch, request, 
            organization_pk=org_1.pk, user_pk=user_1.pk)
