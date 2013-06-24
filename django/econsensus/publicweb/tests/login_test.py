from django.core.urlresolvers import reverse
from django.test import TestCase

from publicweb.models import Decision
from publicweb.tests.open_consent_test_case import EconsensusFixtureTestCase
from publicweb.tests.factories import UserFactory, \
        OrganizationUserFactory, OrganizationOwnerFactory

class LoginTest(EconsensusFixtureTestCase):       
    def test_non_login_is_redirected(self):
        self.client.logout()
        path = reverse('publicweb_decision_create', args=[self.bettysorg.slug, Decision.PROPOSAL_STATUS])
        response = self.client.get(path)
        self.assertEquals(response.status_code, 302)
        
    def test_non_login_directed_to_login(self):
        self.client.logout()
        path = reverse('publicweb_decision_create', args=[self.bettysorg.slug, Decision.PROPOSAL_STATUS])
        response = self.client.get(path)
        self.assertRedirects(response, reverse('auth_login')+'?next='+path)

    def test_add_decision_loads_when_logged_in(self):
        path = reverse('publicweb_decision_create', args=[self.bettysorg.slug, Decision.PROPOSAL_STATUS])
        response = self.client.get(path)
        self.assertEquals(response.status_code, 200)
        
    def test_can_post_through_login(self):
        self.client.logout()
        path = reverse('auth_login')
        page = self.client.get(path)
        
        post_data = self.get_form_values_from_response(page, 1)
        self.assertIn('username', post_data, 'No username field in page content!')
        self.assertIn('password', post_data, 'No password field in page content!')
        post_data['username'] = 'betty'
        post_data['password'] = 'betty'
                
        response = self.client.post(path, post_data, follow=True)

        path = reverse('publicweb_decision_create', args=[self.bettysorg.slug, Decision.PROPOSAL_STATUS])
        response = self.client.get(path, follow=True)
        self.assertEquals(response.status_code, 200)


class LoginTestNonFixture(TestCase):
    """
    Uses factories instead of fixtures for faster tests.
    There's been much confusion over the redirect behaviour upon login, so lets 
    test all cases here.
    """
    def test_single_org_redirect_on_login(self):
        org_user = OrganizationUserFactory()
        self.client.logout()
        org_user.user.set_password('test')
        org_user.user.save()
        response = self.client.post(reverse('auth_login'),
            {'username': org_user.user.username, 'password': 'test'},
            follow = True)
        expected_url = reverse('publicweb_item_list', 
            args=[org_user.organization.slug, Decision.DISCUSSION_STATUS]) 
        self.assertRedirects(response, expected_url)

    def test_single_org_redirect_on_login_with_root_next_query(self):
        org_user = OrganizationUserFactory()
        self.client.logout()
        org_user.user.set_password('test')
        org_user.user.save()
        response = self.client.post(reverse('auth_login')+'?next=/',
            {'username': org_user.user.username, 'password': 'test'},
            follow = True)
        expected_url = reverse('publicweb_item_list', 
            args=[org_user.organization.slug, Decision.DISCUSSION_STATUS]) 
        self.assertRedirects(response, expected_url)
       
    def test_single_org_redirect_on_login_with_orgadd_next_query(self):
        org_user = OrganizationUserFactory()
        self.client.logout()
        org_user.user.set_password('test')
        org_user.user.save()
        response = self.client.post(reverse('auth_login')+'?next=/organizations/add/',
            {'username': org_user.user.username, 'password': 'test'},
            follow = True)
        expected_url = reverse('organization_add') 
        self.assertRedirects(response, expected_url)
       
    def test_multi_org_redirect_on_login(self):
        user = UserFactory()
        org_user1 = OrganizationUserFactory(user=user)
        org_user2 = OrganizationUserFactory(user=user)
        OrganizationOwnerFactory(organization=org_user1.organization)
        OrganizationOwnerFactory(organization=org_user2.organization)
        user.set_password('test')
        user.save()
        response = self.client.post(reverse('auth_login'),
            {'username': user.username, 'password': 'test'},
            follow = True)
        expected_url = reverse('organization_list') 
        self.assertRedirects(response, expected_url)
       
    def test_multi_org_redirect_on_login_with_orglist_next_query(self):
        user = UserFactory()
        org_user1 = OrganizationUserFactory(user=user)
        org_user2 = OrganizationUserFactory(user=user)
        OrganizationOwnerFactory(organization=org_user1.organization)
        OrganizationOwnerFactory(organization=org_user2.organization)
        user.set_password('test')
        user.save()
        response = self.client.post(reverse('auth_login')+'?next=/',
            {'username': user.username, 'password': 'test'},
            follow = True)
        expected_url = reverse('organization_list') 
        self.assertRedirects(response, expected_url)

    def test_multi_org_redirect_on_login_with_other_next_query(self):
        user = UserFactory()
        org_user1 = OrganizationUserFactory(user=user)
        org_user2 = OrganizationUserFactory(user=user)
        user.set_password('test')
        user.save()
        response = self.client.post(reverse('auth_login')+'?next=/organizations/add/',
            {'username': user.username, 'password': 'test'},
            follow = True)
        expected_url = reverse('organization_add') 
        self.assertRedirects(response, expected_url)
