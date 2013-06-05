from django.core.urlresolvers import reverse

from organizations.models import Organization

from decision_test_case import DecisionTestCase

#Put any form tests here
class FormTest(DecisionTestCase):
    
    def test_owner_of_new_org_is_admin_and_editor(self):
        """
        Owner of new organization should be the creating user, and they 
        should be both admin and editor.
        """
        new_org_name = new_org_slug = "neworg"
        self.assertEqual(Organization.objects.filter(slug=new_org_slug).count(), 0, "Organization with this slug already exists")
        path = reverse("organization_add")
        response = self.client.post(
            path, 
            {"name": new_org_name, "slug": new_org_slug, "email": self.charlie.email}
        )
        organizations = Organization.objects.filter(slug=new_org_slug)
        self.assertEqual(organizations.count(), 1, "The Organization wasn't created")
        new_organization = organizations[0]
        self.assertTrue(new_organization.is_owner(self.user), "New Organization has wrong owner")
        self.assertTrue(new_organization.owner.organization_user.is_admin, "Owner of new Organization is not admin")
        self.assertTrue(self.user.has_perm('edit_decisions_feedback', new_organization), "Owner of new Organization is not editor")
