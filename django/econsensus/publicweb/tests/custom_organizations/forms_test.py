from django.test import TestCase
from django.test.client import RequestFactory
from publicweb.tests.factories import UserFactory, \
    OrganizationOwnerFactory, OrganizationFactory

from custom_organizations.forms import CustomOrganizationAddForm,\
    CustomOrganizationUserForm, CustomOrganizationUserAddForm

from django.template.defaultfilters import slugify

from guardian.shortcuts import assign
from django.forms.fields import BooleanField
GUARDIAN_PERMISSION = 'edit_decisions_feedback'


class TestCustomOrganizationAddForm(TestCase):

    def test_save_assigns_the_edit_decisions_feedback_permission_to_user(self):
        """
        Tests that the permission has been assigned to the user. Also
        implicitly tests that the request.user is the user that is assigned
        to the organization.
        """
        # Note: need to set is_active=True otherwise has_perm will be False
        user = UserFactory(is_active=True, email='test@test.com')
        request = RequestFactory()
        # With the new save method, the requesting user is the one who gets the
        # new organization's permissions.
        request.user = user
        form = CustomOrganizationAddForm(request)
        form.cleaned_data = {'name': 'Test'}
        org = form.save()
        self.assertTrue(user.has_perm(GUARDIAN_PERMISSION, org))

    def test_excludes_all_fields_except_organization_name(self):
        """
        The form should only ask for the organization's name. 
        """
        form = CustomOrganizationAddForm(RequestFactory())
        self.assertListEqual(form.fields.keys(), ['name'])

    def test_request_user_is_new_organizations_admin(self):
        """
        We are overriding django-organizations' default behavior to find and
        create users based on the requested email and are making the requesting
        user the default admin of a new organization.
        """
        user = UserFactory()
        request = RequestFactory()
        request.user = user
        form = CustomOrganizationAddForm(request)
        form.cleaned_data = {'name': 'Test'}
        org = form.save()
        self.assertTrue(org.is_admin(user))

    def test_slug_generated_from_name(self):
        """
        An unique slug should be generated from the new Organization's name.
        """
        org_name = "This is my org's name!!"
        expected_slug = slugify(org_name)

        org1 = OrganizationFactory(name=org_name)
        self.assertEqual(org1.slug, expected_slug)

        user = UserFactory()
        request = RequestFactory()
        request.user = user
        form = CustomOrganizationAddForm(request)
        form.cleaned_data = {'name': org_name}
        org = form.save()
        self.assertNotEqual(org.slug, expected_slug)
        self.assertTrue(org.slug.find(expected_slug) >= 0)


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
