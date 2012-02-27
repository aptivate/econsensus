from decision_test_case import DecisionTestCase
from django.core.urlresolvers import reverse
from publicweb.models import Decision, Feedback

#TODO: View tests should not be dependent on redirects from urls.py
#THerefore should not use 'reverse'. Need to create request object...

class ViewTest(DecisionTestCase):

    expected_proposal_key_tuple = ('status_text',)
    expected_proposal_dict_tuple = ({'status_text':'proposal'},)
        
    expected_consensus_key_tuple = ('status_text',)
    expected_consensus_dict_tuple = ({'status_text':'decision'},)
        
    expected_archived_key_tuple = ('status_text',)
    expected_archived_dict_tuple = ({'status_text':'archived'},)
        
    def assert_context_has_key(self, key, url):
        response = self.client.get(url)
        self.assertTrue(key in response.context, 'Key "%s" not found in response.context' % key)

    def assert_context_has_dict(self, dictionary, url):
        response = self.client.get(url)
        self.assertDictContainsSubset(dictionary, response.context, 'warning will robinson!')

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
        