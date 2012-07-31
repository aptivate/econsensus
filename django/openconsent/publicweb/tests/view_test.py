from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from decision_test_case import DecisionTestCase
from publicweb.models import Decision, Feedback

#TODO: View tests should not be dependent on redirects from urls.py
#THerefore should not use 'reverse'. Need to create request object...

class ViewTest(DecisionTestCase):

    expected_proposal_key_tuple = ('tab',)
    expected_proposal_dict_tuple = ({'tab':'proposal'},)
        
    expected_consensus_key_tuple = ('tab',)
    expected_consensus_dict_tuple = ({'tab':'decision'},)
        
    expected_archived_key_tuple = ('tab',)
    expected_archived_dict_tuple = ({'tab':'archived'},)
        
    def assert_context_has_key(self, key, url):
        response = self.client.get(url)
        self.assertTrue(key in response.context, 'Key "%s" not found in response.context' % key)

    def assert_context_has_dict(self, dictionary, url):
        response = self.client.get(url)
        self.assertDictContainsSubset(dictionary, response.context)

    def test_expected_context_keys(self):
        url = reverse('publicweb_item_list', args=['proposal'])
        for key in self.expected_proposal_key_tuple:
            self.assert_context_has_key(key, url)
        url = reverse('publicweb_item_list', args=['decision'])
        for key in self.expected_consensus_key_tuple:
            self.assert_context_has_key(key, url)
        url = reverse('publicweb_item_list', args=['archived'])
        for key in self.expected_archived_key_tuple:
            self.assert_context_has_key(key, url)
        
    def test_expected_context_dict(self):
        url = reverse('publicweb_item_list', args=['proposal'])        
        for dictionary in self.expected_proposal_dict_tuple:
            self.assert_context_has_dict(dictionary, url)        
        url = reverse('publicweb_item_list', args=['decision'])        
        for dictionary in self.expected_consensus_dict_tuple:
            self.assert_context_has_dict(dictionary, url)        
        url = reverse('publicweb_item_list', args=['archived'])        
        for dictionary in self.expected_archived_dict_tuple:
            self.assert_context_has_dict(dictionary, url)                                

    def test_feedback_author_is_assigned(self):
        decision = Decision(description="Test decision")
        decision.save()
        path = reverse('publicweb_feedback_create', args=[decision.id])
        post_dict = {'description': 'Lorem Ipsum','rating': Feedback.COMMENT_STATUS }
        response = self.client.post(path, post_dict)
        self.assertRedirects(response,reverse('publicweb_item_detail', args=[decision.id]))
        feedback = decision.feedback_set.get()
        self.assertEqual(feedback.author, self.user)

    def test_decison_editor_set_on_update(self):
        self.login('Adam')
        decision = self.create_decision_through_browser()
        self.login('Barry')
        decision = self.update_decision_through_browser(decision.id)
        self.assertEquals(self.user, decision.editor)

    def test_all_users_added_to_watchers(self):
        decision = self.create_decision_through_browser()
        all_users = User.objects.all().count()
        self.assertEqual(all_users,decision.watchers.all().count())

    def test_user_can_unwatch(self):
        decision = self.create_decision_through_browser()
        path = reverse('publicweb_decision_update', args=[decision.id])
        post_dict = {'description': decision.description,'status': decision.status, 'watch':False }
        response = self.client.post(path,post_dict)
        self.assertRedirects(response,reverse('publicweb_item_list', args=['proposal']))
        decision = Decision.objects.get(id=decision.id)
        self.assertNotIn(self.user, tuple(decision.watchers.all()))
        
        