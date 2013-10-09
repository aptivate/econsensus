from django.test import TestCase
from guardian.shortcuts import assign_perm

#from organizations.models import OrganizationUser

from publicweb.tests.factories import (OrganizationUserFactory,
                                       OrganizationOwnerFactory)

GUARDIAN_PERMISSION = 'edit_decisions_feedback'


class OrganizationUserMonkeypatchTests(TestCase):

    def test_is_owner_returns_false_when_not_owner(self):
        org_user = OrganizationUserFactory()
        self.assertFalse(org_user.is_owner())

    def test_is_owner_returns_true_when_is_owner(self):
        org_owner = OrganizationOwnerFactory()
        self.assertTrue(org_owner.organization_user.is_owner())

    def test_is_editor_returns_false_when_not_editor(self):
        org_user = OrganizationUserFactory()
        self.assertFalse(org_user.is_editor())

    def test_is_editor_returns_true_when_is_editor(self):
        org_user = OrganizationUserFactory()
        assign_perm(GUARDIAN_PERMISSION, org_user.user, org_user.organization)
        self.assertTrue(org_user.is_editor())

    def test_get_role_returns_owner_when_is_owner(self):
        org_owner = OrganizationOwnerFactory()
        self.assertEqual('owner', org_owner.organization_user.get_role())

    def test_get_role_returns_admin_when_is_admin(self):
        org_user = OrganizationUserFactory(is_admin=True)
        self.assertEqual('admin', org_user.get_role())

    def test_get_role_returns_editor_when_is_editor(self):
        org_user = OrganizationUserFactory()
        assign_perm(GUARDIAN_PERMISSION, org_user.user, org_user.organization)
        self.assertEqual('editor', org_user.get_role())

    def test_get_role_returns_viewer_when_is_viewer(self):
        org_user = OrganizationUserFactory()
        self.assertEqual('viewer', org_user.get_role())
