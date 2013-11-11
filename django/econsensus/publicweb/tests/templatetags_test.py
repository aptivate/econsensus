from django.contrib.comments.models import Comment
from django.test import TestCase

from publicweb.templatetags import publicweb_filters
from publicweb.tests.factories import UserFactory, ObservedItemFactory,\
    DecisionFactory, OrganizationFactory, NoticeTypeFactory
from mock import MagicMock
from publicweb.templatetags.publicweb_filters import is_watching

class CustomTemplateFilterTest(TestCase):
 
    def test_get_user_name_from_comment(self):
        comment = Comment(user=None, user_name='')
        self.assertEqual(publicweb_filters.get_user_name_from_comment(comment), "An Anonymous Contributor")
        comment.user_name = "Harry"
        self.assertEqual(publicweb_filters.get_user_name_from_comment(comment), "Harry")
        user = UserFactory()
        comment.user = user
        self.assertEqual(publicweb_filters.get_user_name_from_comment(comment), user.username)

    def test_get_user_name_for_notification(self):
        user = UserFactory()
        user.username = "bobbins"
        self.assertEquals("bobbins", publicweb_filters.get_user_name_for_notification(user))
        user.first_name = "Robert"
        user.last_name = "Bins"
        self.assertEquals("Robert Bins", publicweb_filters.get_user_name_for_notification(user))
    
    def test_is_watched_returns_true_if_user_in_watchers_list(self):
        user_1 = UserFactory.build(id=1)
        user_2 = UserFactory.build(id=2)
        decision = DecisionFactory.build(organization=OrganizationFactory.build())
        notice_type = NoticeTypeFactory.build()
        observed_item_1 = ObservedItemFactory.build(user=user_1, 
            observed_object=decision, notice_type=notice_type)
        observed_item_2 = ObservedItemFactory.build(user=user_2, 
            observed_object=decision, notice_type=notice_type)
        
        mock_item = MagicMock()
        mock_item.watchers.all = lambda: [observed_item_1, observed_item_2]
        self.assertTrue(is_watching(user_1, mock_item))
    
    def test_is_watched_returns_false_if_user_not_in_watchers_list(self):
        user_1 = UserFactory.build(id=1)
        user_2 = UserFactory.build(id=2)
        user_3 = UserFactory.build(id=3)
        decision = DecisionFactory.build(organization=OrganizationFactory.build())
        notice_type = NoticeTypeFactory.build()
        observed_item_1 = ObservedItemFactory.build(user=user_1, 
            observed_object=decision, notice_type=notice_type)
        observed_item_2 = ObservedItemFactory.build(user=user_2, 
            observed_object=decision, notice_type=notice_type)
        
        mock_item = MagicMock()
        mock_item.watchers.all = lambda: [observed_item_1, observed_item_2]
        self.assertFalse(is_watching(user_3, mock_item))
