from django.test import TestCase
from django.test.client import RequestFactory

from publicweb.tests.factories import OrganizationUserFactory

from custom_organizations.views import CustomOrganizationCreate, \
    CustomOrganizationUserUpdate, CustomOrganizationUserCreate, \
    CustomOrganizationUserDelete
from custom_organizations.forms import CustomOrganizationAddForm, \
    CustomOrganizationUserForm, CustomOrganizationUserAddForm

from guardian.shortcuts import assign
GUARDIAN_PERMISSION = 'edit_decisions_feedback'


class TestCustomOrganizationCreate(TestCase):

    def test_form_class_is_CustomOrganizationAddForm(self):
        custom_org_create_view = CustomOrganizationCreate()
        self.assertEqual(custom_org_create_view.get_form_class(),
                         CustomOrganizationAddForm)


class TestCustomOrganizationUserUpdate(TestCase):

    def test_form_class_is_CustomOrganizationUserForm(self):
        custom_org_user_update_view = CustomOrganizationUserUpdate()
        self.assertEqual(custom_org_user_update_view.get_form_class(),
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
        self.assertEqual(custom_org_user_create_view.get_form_class(),
                         CustomOrganizationUserAddForm)


class TestCustomOrgnizationUserDelete(TestCase):

    def test_delete_deletes_the_unused_permissions(self):
        org_user_delete = CustomOrganizationUserDelete()
        org_user_factory = OrganizationUserFactory()
        org = org_user_factory.organization
        user = org_user_factory.user
        assign(GUARDIAN_PERMISSION, user, org)
        # Confirm permission is True
        self.assertTrue(user.has_perm(GUARDIAN_PERMISSION, org))
        org_user_delete.get_object = lambda: org_user_factory
        request = RequestFactory()
        request.user = user
        org_user_delete.delete(request)
        self.assertFalse(user.has_perm(GUARDIAN_PERMISSION, org))
