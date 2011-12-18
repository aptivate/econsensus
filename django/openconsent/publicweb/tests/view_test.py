from decision_test_case import DecisionTestCase
from django.core.urlresolvers import reverse

#TODO: View tests should not be dependent on redirects from urls.py
#THerefore should not use 'reverse'. Need to create request object...

class ViewTest(DecisionTestCase):

    expected_proposal_key_tuple = ('class', 'page_title','columns')
    expected_proposal_dict_tuple = ({'class':'proposal'},
                                      {'columns': ('id', 'excerpt', 'feedbackcount', 'watchercount', 'deadline')})
        
    expected_consensus_key_tuple = ('class', 'page_title','columns')
    expected_consensus_dict_tuple = ({'class':'decision'},
                                      {'columns': ('id', 'excerpt', 'decided_date', 'review_date')})
        
    expected_archived_key_tuple = ('class', 'page_title','columns')
    expected_archived_dict_tuple = ({'class':'archived'},
                                      {'columns': ('id', 'excerpt', 'created_date', 'archived_date')})
        
    def assert_context_has_key(self, key, url):
        response = self.client.get(url)
        self.assertTrue(key in response.context, 'Key "%s" not found in response.context' % key)

    def assert_context_has_dict(self, dictionary, url):
        response = self.client.get(url)
        self.assertDictContainsSubset(dictionary, response.context, 'warning will robinson!')

    def test_expected_context_keys(self):
        url = reverse('list', args=['proposal'])
        for key in self.expected_proposal_key_tuple:
            self.assert_context_has_key(key, url)
        url = reverse('list', args=['decision'])
        for key in self.expected_consensus_key_tuple:
            self.assert_context_has_key(key, url)
        url = reverse('list', args=['archived'])
        for key in self.expected_archived_key_tuple:
            self.assert_context_has_key(key, url)
        
    def test_expected_context_dict(self):
        url = reverse('list', args=['proposal'])        
        for dictionary in self.expected_proposal_dict_tuple:
            self.assert_context_has_dict(dictionary, url)        
        url = reverse('list', args=['decision'])        
        for dictionary in self.expected_consensus_dict_tuple:
            self.assert_context_has_dict(dictionary, url)        
        url = reverse('list', args=['archived'])        
        for dictionary in self.expected_archived_dict_tuple:
            self.assert_context_has_dict(dictionary, url)                                
