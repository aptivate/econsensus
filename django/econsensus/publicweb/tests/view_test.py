from django.core.urlresolvers import reverse
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from decision_test_case import DecisionTestCase
from publicweb.models import Decision, Feedback
from organizations.models import Organization, OrganizationUser

#TODO: View tests should not be dependent on redirects from urls.py
#THerefore should not use 'reverse'. Need to create request object...


class ViewTest(DecisionTestCase):
    fixtures = ['organizations.json', 'users.json', 'decisions.json']

    expected_proposal_key_tuple = ('tab',)
    expected_proposal_dict_tuple = ({'tab': 'proposal'},)

    expected_consensus_key_tuple = ('tab',)
    expected_consensus_dict_tuple = ({'tab': 'decision'},)

    expected_archived_key_tuple = ('tab',)
    expected_archived_dict_tuple = ({'tab': 'archived'},)

    def assert_context_has_key(self, key, url):
        response = self.client.get(url)
        self.assertTrue(key in response.context,
                        'Key "%s" not found in response.context' % key)

    def assert_context_has_dict(self, dictionary, url):
        response = self.client.get(url)
        self.assertDictContainsSubset(dictionary, response.context)

    def test_expected_context_keys(self):
        url = reverse('publicweb_item_list',
                      args=[self.bettysorg.slug, 'proposal'])
        for key in self.expected_proposal_key_tuple:
            self.assert_context_has_key(key, url)
        url = reverse('publicweb_item_list',
                      args=[self.bettysorg.slug, 'decision'])
        for key in self.expected_consensus_key_tuple:
            self.assert_context_has_key(key, url)
        url = reverse('publicweb_item_list',
                      args=[self.bettysorg.slug, 'archived'])
        for key in self.expected_archived_key_tuple:
            self.assert_context_has_key(key, url)

    def test_expected_context_dict(self):
        url = reverse('publicweb_item_list',
                      args=[self.bettysorg.slug, 'proposal'])
        for dictionary in self.expected_proposal_dict_tuple:
            self.assert_context_has_dict(dictionary, url)
        url = reverse('publicweb_item_list',
                      args=[self.bettysorg.slug, 'decision'])
        for dictionary in self.expected_consensus_dict_tuple:
            self.assert_context_has_dict(dictionary, url)
        url = reverse('publicweb_item_list',
                      args=[self.bettysorg.slug, 'archived'])
        for dictionary in self.expected_archived_dict_tuple:
            self.assert_context_has_dict(dictionary, url)

    def test_feedback_author_is_assigned(self):
        decision = self.create_and_return_decision()
        path = reverse('publicweb_feedback_create', args=[decision.id])
        post_dict = {'description': 'Lorem Ipsum',
                     'rating': Feedback.COMMENT_STATUS}
        response = self.client.post(path, post_dict)
        self.assertRedirects(response,
                             reverse('publicweb_item_detail',
                                     args=[decision.id]))
        feedback = decision.feedback_set.get()
        self.assertEqual(feedback.author, self.user)

    def test_decison_editor_set_on_update(self):
        self.login('andy')
        decision = self.create_decision_through_browser()
        self.login('betty')
        decision = self.update_decision_through_browser(decision.id)
        self.assertEquals(self.user, decision.editor)

        admin_user = User.objects.filter(is_staff=True)[0]
        self.login(admin_user.username)
        ma = ModelAdmin(Decision, AdminSite())
        data = ma.get_form(None)(instance=decision).initial
        for key, value in data.items():
            if value == None:
                data[key] = u''
        man_data = {
            'feedback_set-TOTAL_FORMS': u'1', 
            'feedback_set-INITIAL_FORMS': u'0', 
            'feedback_set-MAX_NUM_FORMS': u''
        }
        data.update(man_data)
        url = reverse('admin:publicweb_decision_change', args=[decision.id])
        response = self.client.post(url, data, follow=True)
        self.assertEquals(response.status_code, 200)
        decision = Decision.objects.get(id=decision.id)
        self.assertEquals(decision.editor, admin_user)

    def test_all_users_added_to_watchers(self):
        decision = self.create_decision_through_browser()
        all_users = User.objects.all().exclude(is_active=False).count()
        self.assertEqual(all_users, decision.watchers.all().count())

    def test_user_can_unwatch(self):
        decision = self.create_decision_through_browser()
        path = reverse('publicweb_decision_update', args=[decision.id])
        post_dict = {'description': decision.description,
                     'status': decision.status,
                     'watch': False}
        response = self.client.post(path, post_dict)
        self.assertRedirects(response,
                             reverse('publicweb_item_list',
                                     args=[self.bettysorg.slug,
                                           'proposal']))
        decision = Decision.objects.get(id=decision.id)
        self.assertNotIn(self.user, tuple(decision.watchers.all()))

    def test_redirect_for_one_organization(self):
        '''
        if the user is a member of only one organization then on login
        they should be redirected to the proposal page for that one
        organization and not the organization list page.
        '''
        arbury = User.objects.create_user('arbury', password='arbury')
        org = Organization.active.latest('id')
        OrganizationUser.objects.create(user=arbury,
                                        organization=org,
                                        is_admin=False)
        self.login('arbury')
        path = reverse('auth_login')
        # Known bug when next param supplied - see
        # https://aptivate.kanbantool.com/boards/5986-econsensus#tasks-1251883
        #post_dict = {'username': 'arbury',
        #             'password': 'arbury',
        #             'next': '/organizations/'}
        post_dict = {'username': 'arbury', 'password': 'arbury'}
        response = self.client.post(path, post_dict, follow=True)
        self.assertRedirects(response,
                             reverse('publicweb_item_list',
                                     args=[org.slug, 'proposal']))

    def test_redirect_for_many_organizations(self):
        '''
        if the user is a member of many organizations then on login
        they should be redirected to the organization list page
        which shows all the organizations to which they belong.
        '''
        arbury = User.objects.create_user('arbury', password='arbury')
        orgs = Organization.active.all()[:2]
        OrganizationUser.objects.create(user=arbury,
                                        organization=orgs[0],
                                        is_admin=False)
        OrganizationUser.objects.create(user=arbury,
                                        organization=orgs[1],
                                        is_admin=False)
        self.login('arbury')
        path = reverse('auth_login')
        post_dict = {'username': 'arbury', 'password': 'arbury'}
        response = self.client.post(path, post_dict, follow=True)
        self.assertRedirects(response, reverse('organization_list'))
