from django.test import TestCase
from django.test.client import RequestFactory
from publicweb.tests.factories import UserFactory, \
    OrganizationOwnerFactory, OrganizationFactory

from custom_organizations.forms import CustomOrganizationAddForm,\
    CustomOrganizationUserForm, CustomOrganizationUserAddForm

from guardian.shortcuts import assign
from django.forms.fields import BooleanField

GUARDIAN_PERMISSION = 'edit_decisions_feedback'


class TestCustomOrganizationAddForm(TestCase):

    def test_save_assigns_the_edit_decisions_feedback_permission_to_user(self):
        # Note need to set is_active=True otherwise has_perm will be False
        user = UserFactory(is_active=True, email='test@test.com')
        form = CustomOrganizationAddForm(RequestFactory())
        form.cleaned_data = {
            'email': user.email,
            'name': 'Test',
            'slug': '',
        }
        form.request = RequestFactory()
        form.request.user = UserFactory.build()  # Different user
        org = form.save()
        self.assertTrue(user.has_perm(GUARDIAN_PERMISSION, org))


class TestCustomOrganizationUserForm(TestCase):

    # What's a good way to check the required property?
    def test_new_is_editor_field_is_present_and_boolean_type(self):
        form = CustomOrganizationUserForm()
        self.assertTrue('is_editor' in form.fields)
        self.assertTrue(isinstance(form.fields['is_editor'],
                                   BooleanField))

    def test_is_editor_is_true_adds_permission_to_instance(self):
        org_owner_factory = OrganizationOwnerFactory()
        org_user = org_owner_factory.organization_user
        user = org_user.user
        org = org_user.organization
        # Check that permission is False
        self.assertFalse(user.has_perm(GUARDIAN_PERMISSION, org))
        # Need to pass {'is_admin': True} for clean_is_admin to validate
        form = CustomOrganizationUserForm(data={'is_admin': True},
                                          instance=org_user)
        form.cleaned_data = {'is_editor': True}
        form.save()
        # Now it should be True
        self.assertTrue(user.has_perm(GUARDIAN_PERMISSION, org))

    def test_is_editor_is_false_removes_permission_from_instance(self):
        org_owner_factory = OrganizationOwnerFactory()
        org_user = org_owner_factory.organization_user
        user = org_user.user
        org = org_user.organization
        assign(GUARDIAN_PERMISSION, user, org)
        # Confirm permission is True
        self.assertTrue(user.has_perm(GUARDIAN_PERMISSION, org))
        form = CustomOrganizationUserForm(data={'is_admin': True},
                                          instance=org_user)
        form.cleaned_data = {'is_editor': False}
        form.save()
        # Now it should be False
        self.assertFalse(user.has_perm(GUARDIAN_PERMISSION, org))


class TestCustomOrganizationUserAddForm(TestCase):
    """Form class for adding OrganizationUsers to an existing Organization"""

    # What's a good way to check the required property?
    def test_new_is_editor_field_is_present_and_boolean_type(self):
        request = RequestFactory()
        organization = OrganizationFactory()
        form = CustomOrganizationUserAddForm(request, organization)
        self.assertTrue('is_editor' in form.fields)
        self.assertTrue(isinstance(form.fields['is_editor'],
                                   BooleanField))

    def test_is_editor_is_true_adds_permission_to_instance(self):
        org = OrganizationFactory()
        user = UserFactory(email='test@test.com')
        # Check that permission is False
        self.assertFalse(user.has_perm(GUARDIAN_PERMISSION, org))
        # Need to pass {'is_admin': True} for clean_is_admin to validate
        request = RequestFactory()
        request.user = UserFactory.build()
        form = CustomOrganizationUserAddForm(request, org)
        form.cleaned_data = {'is_editor': True,
                             'is_admin': True,
                             'email': user.email}
        form.save()
        # Now it should be True
        self.assertTrue(user.has_perm(GUARDIAN_PERMISSION, org))

    def test_is_editor_is_false_removes_permission_from_instance(self):
        org = OrganizationFactory()
        user = UserFactory(email='test@test.com')
        assign(GUARDIAN_PERMISSION, user, org)
        # Confirm permission is True
        self.assertTrue(user.has_perm(GUARDIAN_PERMISSION, org))
        request = RequestFactory()
        request.user = UserFactory.build()
        form = CustomOrganizationUserAddForm(request, org)
        form.cleaned_data = {'is_editor': False,
                             'is_admin': True,
                             'email': user.email}
        form.save()
        # Now it should be False
        self.assertFalse(user.has_perm(GUARDIAN_PERMISSION, org))
