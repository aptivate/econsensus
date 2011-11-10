from decision_test_case import DecisionTestCase
from django.core.urlresolvers import reverse

#TODO: View tests should not be dependent on redirects from urls.py
#THerefore should not use 'reverse'. Need to create request object...

class ViewTest(DecisionTestCase):

    expected_key_tuple = ('class', 'page_title','columns')
    expected_dict_tuple = ({'class':'consensus'},)
        
    def assert_context_has_key(self, key):
        response = self.client.get(reverse('list', args=['consensus']))
        self.assertTrue(key in response.context, 'Key "%s" not found in response.context' % key)

    def assert_context_has_dict(self, dictionary):
        response = self.client.get(reverse('list', args=['consensus']))
        self.assertDictContainsSubset(dictionary, response.context, 'warning will robinson!')

    def test_expected_context_keys(self):
        for key in self.expected_key_tuple:
            self.assert_context_has_key(key)
        
    def test_expected_context_dict(self):
        for dictionary in self.expected_dict_tuple:
            self.assert_context_has_dict(dictionary)        