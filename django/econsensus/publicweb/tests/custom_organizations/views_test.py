from django.test import TestCase
from django.test.client import RequestFactory

from publicweb.tests.factories import OrganizationUserFactory, DecisionFactory,\
    ObservedItemFactory, UserFactory, FeedbackFactory

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
    def test_is_admin_detects_organization_admins(self):
        org_user_delete_view = CustomOrganizationUserDelete()
        org_user = OrganizationUserFactory(is_admin=True)
        org = org_user.organization
        user = org_user.user
        request = RequestFactory()
        request.user = user
        self.assertTrue(org_user_delete_view._is_admin(request, org.pk))
    
    def test_is_admin_detects_superusers(self):
        org_user_delete_view = CustomOrganizationUserDelete()
        org_user = OrganizationUserFactory()
        org = org_user.organization
        user = org_user.user
        user.is_superuser = True
        user.save()
        request = RequestFactory()
        request.user = user
        self.assertTrue(org_user_delete_view._is_admin(request, org.pk))
    
    def test_is_admin_doesnt_detect_normal_users(self):
        org_user_delete_view = CustomOrganizationUserDelete()
        org_user = OrganizationUserFactory()
        org = org_user.organization
        user = org_user.user
        request = RequestFactory()
        request.user = user
        self.assertFalse(org_user_delete_view._is_admin(request, org.pk))
    
    def test_is_current_user_detects_when_user_is_same_as_requests(self):
        org_user_delete_view = CustomOrganizationUserDelete()
        
        user = UserFactory()
        
        request = RequestFactory()
        request.user = user

        self.assertTrue(org_user_delete_view._is_current_user(request, user.id))
        
    def test_is_current_user_detects_when_user_is_different_from_requests(self):
        org_user_delete_view = CustomOrganizationUserDelete()
        
        user_1 = UserFactory()
        user_2 = UserFactory()
        request = RequestFactory()
        request.user = user_2

        self.assertFalse(
            org_user_delete_view._is_current_user(request, user_1.id))
    
    def test_organisation_user_delete_view_is_accessible_to_admin(self):
        org_user_delete_view = CustomOrganizationUserDelete()
        org_user = OrganizationUserFactory(is_admin=True)
        org = org_user.organization
        user_1 = org_user.user
        
        user_2 = UserFactory()
        assign_perm(GUARDIAN_PERMISSION, user_1, org)
        request = RequestFactory().post("/", {'submit': "Delete"})
        request.user = user_1
        
        org_user_delete_view.get_object = lambda: org_user
            
        response = org_user_delete_view.dispatch(
                 request, organization_pk=org.pk, user_pk=user_2.pk)
        
        self.assertEqual(
         reverse('organization_user_list', args=[org.pk]), response['Location']
            )
    
    def test_organisation_user_delete_view_is_accessible_to_superuser(self):
        org_user_delete_view = CustomOrganizationUserDelete()
        org_user = OrganizationUserFactory()
        org = org_user.organization
        user_1 = org_user.user
        user_1.is_superuser = True
        user_1.save()
        
        user_2 = UserFactory()
        assign_perm(GUARDIAN_PERMISSION, user_1, org)
        request = RequestFactory().post("/", {'submit': "Delete"})
        request.user = user_1
        
        org_user_delete_view.get_object = lambda: org_user
            
        response = org_user_delete_view.dispatch(
                 request, organization_pk=org.pk, user_pk=user_2.pk)
        
        self.assertEqual(
         reverse('organization_user_list', args=[org.pk]), response['Location']
            )
    
    def test_organisation_user_delete_view_lets_user_delete_themself(self):
        org_user_delete_view = CustomOrganizationUserDelete()
        org_user = OrganizationUserFactory()
        org = org_user.organization
        user = org_user.user
        
        assign_perm(GUARDIAN_PERMISSION, user, org)
        request = RequestFactory().post("/", {'submit': "Delete"})
        request.user = user
        
        org_user_delete_view.get_object = lambda: org_user
            
        response = org_user_delete_view.dispatch(
                 request, organization_pk=org.pk, user_pk=user.pk)
        
        self.assertEqual(
         reverse('organization_user_list', args=[org.pk]), response['Location']
            )
        
    def test_organisation_user_delete_view_doesnt_let_user_delete_others(self):
        org_user_delete_view = CustomOrganizationUserDelete()
        org_user = OrganizationUserFactory()
        org = org_user.organization
        user_1 = org_user.user
        
        user_2 = UserFactory()
        assign_perm(GUARDIAN_PERMISSION, user_1, org)
        request = RequestFactory().post("/", {'submit': "Delete"})
        request.user = user_1
        org_user_delete_view.get_object = lambda: org_user
        
        self.assertRaises(Http404, org_user_delete_view.dispatch, request, 
            organization_pk=unicode(org.pk), user_pk=unicode(user_2.pk)) 
    
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
    
    def test_delete_stops_users_watching_feedback_for_the_organization(self):
        org_user_delete_view = CustomOrganizationUserDelete()
        feedback = FeedbackFactory()
        observed_item = ObservedItemFactory(observed_object=feedback)
        org = observed_item.observed_object.decision.organization
        user = feedback.author
        org_user = OrganizationUserFactory(organization=org, user=user)
        org_user_delete_view.get_object = lambda: org_user
        request = RequestFactory()
        request.user = user
        org_user_delete_view.delete(request)
        # Two observed items were created for different users
        # Only the second one should remain after the delete request
        self.assertSequenceEqual([observed_item], feedback.watchers.all())
        

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
