from open_consent_test_case import EconsensusFixtureTestCase

from publicweb.templatetags import publicweb_filters
from django.contrib.comments.models import Comment

# test custom template filters
class CustomTemplateFilterTest(EconsensusFixtureTestCase):
 
    def test_get_user_name_from_comment(self):
        c = Comment()
        c.user = self.betty
        self.assertEqual(publicweb_filters.get_user_name_from_comment(c), "betty")
        c.user=None
        self.assertEqual(publicweb_filters.get_user_name_from_comment(c), "An Anonymous Contributor")
        c.user_name = "Harry"
        self.assertEqual(publicweb_filters.get_user_name_from_comment(c), "Harry")
