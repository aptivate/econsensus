from django.test import TestCase
from django.test.client import RequestFactory
from publicweb.tests.factories import UserFactory, \
    OrganizationOwnerFactory, OrganizationFactory

from custom_organizations.forms import CustomOrganizationAddForm,\
    CustomOrganizationUserForm, CustomOrganizationUserAddForm, \
    CustomOrganizationForm, ChangeOwnerForm

from django.template.defaultfilters import slugify

from guardian.shortcuts import assign_perm
from django.forms.fields import BooleanField, ChoiceField
GUARDIAN_PERMISSION = 'edit_decisions_feedback'


class TestCustomOrganizationForm(TestCase):

    def test_excludes_all_fields_except_organization_name(self):
        """
        The form should only ask for the organization's name. 
        """
        form = CustomOrganizationForm(RequestFactory())
        self.assertListEqual(form.fields.keys(), ['name'])

    
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
        An unique slug should be generated for each Organization from its name.
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
        org2 = form.save()
        self.assertNotEqual(org2.slug, org1.slug)
        self.assertTrue(org2.slug.startswith(org1.slug))


class TestCustomOrganizationUserForm(TestCase):

    def test_user_type_field_is_present_and_boolean_type(self):
        """
        Check that the form contains a boolean for is_editor.
        """
        form = CustomOrganizationUserForm()
        self.assertIn('user_type', form.fields)
        self.assertTrue(
            isinstance(form.fields['user_type'], ChoiceField)
        )

    def test_user_type_editor_adds_permission_to_instance(self):
        """
        When editor is selected, the correct permission is set for that user
        for that organization.
        """
        org_owner = OrganizationOwnerFactory()
        org_user = org_owner.organization_user
        user = org_user.user
        org = org_user.organization
        # Check the user doesn't have the permission
        self.assertFalse(user.has_perm(GUARDIAN_PERMISSION, org))
        # Need to pass {'is_admin': True} for clean_is_admin to validate
        form = CustomOrganizationUserForm(instance=org_user)
        form.cleaned_data = {'user_type': 'editor'}
        form.save()
        # Now they should have the permission
        self.assertTrue(user.has_perm(GUARDIAN_PERMISSION, org))

    def test_user_type_viewer_removes_permission_from_instance(self):
        """
        When is_editor gets unticked, the permission is removed. 
        Also implicitly tests is_editor form field's required property because 
        for a BooleanField, False is empty.
        """
        org_owner = OrganizationOwnerFactory()
        org_user = org_owner.organization_user
        user = org_user.user
        org = org_user.organization
        assign_perm(GUARDIAN_PERMISSION, user, org)
        # Confirm user has the permission
        self.assertTrue(user.has_perm(GUARDIAN_PERMISSION, org))
        form = CustomOrganizationUserForm(instance=org_user)
        form.cleaned_data = {'user_type': 'viewer'}
        form.save()
        # Now they shouldn't have the permission
        self.assertFalse(user.has_perm(GUARDIAN_PERMISSION, org))


class TestCustomOrganizationUserAddForm(TestCase):
    """Form class for adding OrganizationUsers to an existing Organization"""

    def test_user_type_field_is_present_and_choice_type(self):
        """
        Check that the form contains a boolean for user_type, and that it has
        the expected initial value.
        """
        request = RequestFactory()
        organization = OrganizationFactory()
        form = CustomOrganizationUserAddForm(request, organization)
        self.assertIn('user_type', form.fields)
        self.assertTrue(
            isinstance(form.fields['user_type'], ChoiceField)
        )

    def test_user_type_editor_adds_permission_to_instance(self):
        """
        When user_type is editor, the correct permission is set for that user
        for that organization.
        """
        org = OrganizationFactory()
        user = UserFactory(email='test@test.com')
        # Check the user doesn't have the permission
        self.assertFalse(user.has_perm(GUARDIAN_PERMISSION, org))
        request = RequestFactory()
        request.user = UserFactory.build()
        form = CustomOrganizationUserAddForm(request, org)
        form.cleaned_data = {'user_type' : 'editor',
                             'email': user.email}
        form.save()
        # Now they should have the permission
        self.assertTrue(user.has_perm(GUARDIAN_PERMISSION, org))

    def test_user_type_viewer_removes_permission_from_instance(self):
        """
        When user_type is set to viewer, the permission is removed. 
        """
        org = OrganizationFactory()
        user = UserFactory(email='test@test.com')
        assign_perm(GUARDIAN_PERMISSION, user, org)
        # Confirm the user has the permission
        self.assertTrue(user.has_perm(GUARDIAN_PERMISSION, org))
        request = RequestFactory()  
        request.user = UserFactory.build()
        form = CustomOrganizationUserAddForm(request, org)
        form.cleaned_data = {'user_type': 'viewer',
                             'email': user.email}
        form.save()
        # Now they shouldn't have the permission
        self.assertFalse(user.has_perm(GUARDIAN_PERMISSION, org))


class TestCustomOrganizationChangeOwnerForm(TestCase):

    def test_current_org_pk_is_correctly_set_when_kwarg_is_passed(self):
        org_owner = OrganizationOwnerFactory()
        org_user = org_owner.organization_user
        org = org_user.organization

        changeownerform = ChangeOwnerForm(current_org_pk=org.pk)
        self.assertEqual(changeownerform.fields['organization_user'].queryset.get().pk, org_user.pk)
