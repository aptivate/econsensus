from django.contrib.auth.models import Permission
from decision_test_case import DecisionTestCase
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from guardian.models import UserObjectPermission
from guardian.shortcuts import remove_perm
from organizations.models import Organization

from publicweb.models import Decision

#does Organization have permission 'editor'
class OrganizationTest(DecisionTestCase):

    def test_organization_has_editor_permission(self):
        content_type = ContentType.objects.get(app_label='organizations', model='organization')
        try:
            Permission.objects.get(codename='edit_decisions_feedback',
                                   content_type=content_type)
        except:
            self.fail("Could not find 'edit_decisions_feedback' permission on model 'Organizations'")
    
    def test_decision_create_restricted_if_no_editor_perm_for_specific_organization(self):
        #first remove the permission and check the removal worked
        remove_perm('edit_decisions_feedback', self.betty, self.bettysorg)
        self.assertFalse(self.betty.has_perm('edit_decisions_feedback', self.bettysorg))
        
        #assert that creating a decision gives a 403
        path = reverse('publicweb_decision_create', args=[self.bettysorg.slug, Decision.PROPOSAL_STATUS])
        response = self.client.get(path)
        self.assertEquals(response.status_code, 403)
        #give perm
        UserObjectPermission.objects.assign('edit_decisions_feedback', user=self.betty, obj=self.bettysorg)
        # get a 200
        response = self.client.get(path)
        self.assertEquals(response.status_code, 200)

        # confirm 403 for different org    
        bettys_unauthed_org = Organization.objects.get_for_user(self.betty)[1]
        path = reverse('publicweb_decision_create', args=[bettys_unauthed_org.slug, Decision.PROPOSAL_STATUS])
        response = self.client.get(path)
        self.assertEquals(response.status_code, 403)        
               