from django.contrib.auth.models import Permission
from decision_test_case import DecisionTestCase
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from guardian.shortcuts import remove_perm, assign
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
    
    def test_decision_create_restricted(self):
        '''
        Decision create should be restricted to those with the organizations editor permission
        '''
        #first remove the permission
        remove_perm('edit_decisions_feedback', self.betty, self.bettysorg)
        
        #assert that creating a decision gives a 403
        path = reverse('publicweb_decision_create', args=[self.bettysorg.slug, Decision.PROPOSAL_STATUS])
        response = self.client.get(path)
        self.assertEquals(response.status_code, 403)
        #give perm
        assign('edit_decisions_feedback', self.betty, self.bettysorg)
        # get a 200
        response = self.client.get(path)
        self.assertEquals(response.status_code, 200)

        # confirm 403 for different org    
        bettys_unauthed_org = Organization.objects.get_for_user(self.betty)[1]
        path = reverse('publicweb_decision_create', args=[bettys_unauthed_org.slug, Decision.PROPOSAL_STATUS])
        response = self.client.get(path)
        self.assertEquals(response.status_code, 403)        
    
    def test_decision_update_restricted(self):
        '''
        Decision update should be restricted to those with the organizations editor permission
        '''
        
        #setup
        decision = self.create_and_return_decision()
        #first remove the permission        
        remove_perm('edit_decisions_feedback', self.betty, self.bettysorg)
        #assert that creating a decision gives a 403
        path = reverse('publicweb_decision_update', args=[decision.id])
        response = self.client.get(path)
        self.assertEquals(response.status_code, 403)
        #give perm
        assign('edit_decisions_feedback', self.betty, self.bettysorg)
        # get a 200
        response = self.client.get(path)
        self.assertEquals(response.status_code, 200)
        
    def test_feedback_create_restricted(self):
        '''
        Feedback create should be restricted to those with the organizations editor permission
        '''

        #setup
        decision = self.create_and_return_decision()        
        #first remove the permission
        remove_perm('edit_decisions_feedback', self.betty, self.bettysorg)
        
        #assert that creating feedback gives a 403
        path = reverse('publicweb_feedback_create', args=[decision.id])
        response = self.client.get(path)
        self.assertEquals(response.status_code, 403)
        #give perm
        assign('edit_decisions_feedback', self.betty, self.bettysorg)
        # get a 200
        response = self.client.get(path)
        self.assertEquals(response.status_code, 200)     
            
    def test_feedback_update_restricted(self):
        '''
        Feedback update should be restricted to those with the organizations editor permission
        '''
        #setup
        feedback = self.create_and_return_feedback()
        #first remove the permission        
        remove_perm('edit_decisions_feedback', self.betty, self.bettysorg)
        #assert that creating a decision gives a 403
        path = reverse('publicweb_feedback_update', args=[feedback.id])
        response = self.client.get(path)
        self.assertEquals(response.status_code, 403)
        #give perm
        assign('edit_decisions_feedback', self.betty, self.bettysorg)
        # get a 200
        response = self.client.get(path)
        self.assertEquals(response.status_code, 200)

    def test_org_details_page_restricted(self):
        '''
        Organization details page should be restricted to admin users.
        '''
        # non-admin user gets a 403
        path = reverse('organization_detail', args=[self.bettysorg.id])
        self.login('charlie')
        response = self.client.get(path)
        self.assertEqual(response.status_code, 403)
        # admin user gets a 200
        self.login('betty')
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
