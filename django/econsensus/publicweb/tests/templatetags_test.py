from django.contrib.comments.models import Comment
from django.test import TestCase

from publicweb.templatetags import publicweb_filters
from publicweb.tests.factories import UserFactory

class CustomTemplateFilterTest(TestCase):
 
    def test_get_user_name_from_comment(self):
        comment = Comment(user=None, user_name='')
        self.assertEqual(publicweb_filters.get_user_name_from_comment(comment), "An Anonymous Contributor")
        comment.user_name = "Harry"
        self.assertEqual(publicweb_filters.get_user_name_from_comment(comment), "Harry")
        user = UserFactory()
        comment.user = user
        self.assertEqual(publicweb_filters.get_user_name_from_comment(comment), user.username)
