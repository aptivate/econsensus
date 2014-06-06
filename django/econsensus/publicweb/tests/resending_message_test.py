from django.test.testcases import SimpleTestCase
from mock import patch, Mock
from publicweb.extra_models import FEEDBACK_ADDED_NOTIFICATIONS,\
    NotificationSettings, FEEDBACK_MAJOR_CHANGES
from django_dynamic_fixture import N
from django.contrib.auth.models import User
from publicweb.models import Decision, additional_message_required

def get_or_create(**kwargs):
    return N(
                    NotificationSettings, 
                    notification_level=FEEDBACK_ADDED_NOTIFICATIONS
            ), True

class ResendingMessageTest(SimpleTestCase):
    @patch('publicweb.models.NotificationSettings.objects', 
           new=Mock(get_or_create=get_or_create)
    )
    @patch('publicweb.models.notification', 
           new=Mock(is_observing=lambda a,b: False))
    def test_message_required_if_major_changes_only_user_watches_adds_comment(self):
        user_1 = N(User, id=1)
        decision = N(Decision, author=user_1, editor=user_1, id=1)
        decision.watchers = []
        self.assertTrue(
            additional_message_required(
                user_1, decision, FEEDBACK_MAJOR_CHANGES
            )
        )
    
    @patch('publicweb.models.NotificationSettings.objects', 
       new=Mock(get_or_create=lambda organization, user: (
                N(
                  NotificationSettings, 
                  notification_level=FEEDBACK_MAJOR_CHANGES
                ), 
                True
            )
        )
    )
    @patch('publicweb.models.notification', 
         new=Mock(is_observing=lambda a,b: False))
    def test_message_not_required_if_feedback_major_notification_user_watches_adds_comment(self):
        user_1 = N(User, id=1)
        decision = N(Decision, author=user_1, editor=user_1, id=1)
        
        self.assertFalse(
            additional_message_required(
                user_1, decision, FEEDBACK_MAJOR_CHANGES
            )
        )
    
    @patch('publicweb.models.NotificationSettings.objects', 
           new=Mock(get_or_create=get_or_create)
    )
    @patch('publicweb.models.notification', 
           new=Mock(is_observing=lambda a,b: True))
    def test_message_not_required_if_user_already_observing(self):
        user_1 = N(User, id=1)
        decision = N(Decision, author=user_1, editor=user_1, id=1)
        
        self.assertFalse(
            additional_message_required(
                user_1, decision, FEEDBACK_MAJOR_CHANGES
            )
        )
    
    @patch('publicweb.models.NotificationSettings.objects', 
           new=Mock(get_or_create=get_or_create)
    )
    @patch('publicweb.models.notification', 
           new=Mock(is_observing=lambda a,b: False))
    def test_message_required_if_user_not_already_observing(self):
        user_1 = N(User, id=1)
        decision = N(Decision, author=user_1, editor=user_1, id=1)
        
        self.assertTrue(
            additional_message_required(
                user_1, decision, FEEDBACK_MAJOR_CHANGES
            )
        )
