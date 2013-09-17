from django.test.testcases import SimpleTestCase
from publicweb.tests.factories import (NotificationSettingsFactory,
    DecisionFactory, FeedbackFactory, CommentFactory, UserFactory,
    OrganizationFactory)
from publicweb.models import (NO_NOTIFICATIONS, MAIN_ITEMS_NOTIFICATIONS_ONLY,
    FEEDBACK_ADDED_NOTIFICATIONS, FEEDBACK_MAJOR_CHANGES, NotificationSettings)
from mock import patch, MagicMock
from publicweb.observation_manager import ObservationManager
from signals.management import (DECISION_STATUS_CHANGE, FEEDBACK_CHANGE, 
    DECISION_NEW, FEEDBACK_NEW, DECISION_CHANGE, COMMENT_NEW, COMMENT_CHANGE,
    MINOR_CHANGE)

def create_fake_settings(**kwargs):
    if not "notification_level" in kwargs:
        kwargs["notification_level"] = NO_NOTIFICATIONS
    return NotificationSettingsFactory.build(**kwargs) 

class ObservationManagerTest(SimpleTestCase):
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_observer_not_created_for_no_notifications_level(self, observed_item):
        settings = create_fake_settings()
        settings_handler = ObservationManager()

        settings_handler.update_observers(
             settings, DecisionFactory.build(), DECISION_NEW, 'post_save' 
        )
        
        self.assertFalse(observed_item.called)

    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_new_decision_observer_created_for_main_items_notification_level(self, observed_item):
        settings = create_fake_settings(
            notification_level=MAIN_ITEMS_NOTIFICATIONS_ONLY
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, DecisionFactory.build(), DECISION_NEW, 'post_save' 
        )
        
        self.assertTrue(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_decision_status_change_observer_created_for_main_items_notification_level(self, observed_item):
        settings = create_fake_settings(
             notification_level=MAIN_ITEMS_NOTIFICATIONS_ONLY
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, DecisionFactory.build(), DECISION_STATUS_CHANGE, 
             'post_save' 
        )
        
        self.assertTrue(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_decision_change_observer_not_created_for_main_items_notification_level(self, observed_item):
        settings = create_fake_settings(
            notification_level=MAIN_ITEMS_NOTIFICATIONS_ONLY
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers( 
            settings, DecisionFactory.build(), DECISION_CHANGE, 'post_save' 
        )
        
        self.assertFalse(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_feedback_created_observer_not_created_for_main_items_notification_level(self, observed_item):
        settings = create_fake_settings(
             notification_level=MAIN_ITEMS_NOTIFICATIONS_ONLY
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers( 
             settings, FeedbackFactory.build(), FEEDBACK_NEW, 'post_save' 
        )
        
        self.assertFalse(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_decision_changed_observer_created_for_feedback_added_level(self, observed_item):
        settings = create_fake_settings(
            notification_level=FEEDBACK_ADDED_NOTIFICATIONS
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers( 
            settings, DecisionFactory.build(), DECISION_CHANGE, 'post_save' 
        )
        
        self.assertTrue(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_feedback_created_observer_created_for_feedback_added_notification_level(self, observed_item):
        settings = create_fake_settings(
             notification_level=FEEDBACK_ADDED_NOTIFICATIONS
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, FeedbackFactory.build(), FEEDBACK_NEW, 'post_save' 
        )
        
        self.assertTrue(observed_item.called)
        
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_feedback_changed_observer_not_added_for_feedback_added_notification_level(self, observed_item):
        settings = create_fake_settings(
             notification_level=FEEDBACK_ADDED_NOTIFICATIONS
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, FeedbackFactory.build(), FEEDBACK_CHANGE, 'post_save' 
        )
        
        self.assertFalse(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_feedback_changed_observer_added_for_major_changes_notification_level(self, observed_item):
        settings = create_fake_settings(
             notification_level=FEEDBACK_MAJOR_CHANGES
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, FeedbackFactory.build(), FEEDBACK_CHANGE, 'post_save' 
        )
        
        self.assertTrue(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_minor_change_observer_not_added_for_major_changes_notification_level(self, observed_item):
        settings = create_fake_settings(
             notification_level=FEEDBACK_MAJOR_CHANGES
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, FeedbackFactory.build(), MINOR_CHANGE, 'post_save' 
        )
        
        self.assertFalse(observed_item.called)
        
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_comment_created_observer_added_for_major_changes_notification_level(self, observed_item):
        settings = create_fake_settings(
             notification_level=FEEDBACK_MAJOR_CHANGES
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, FeedbackFactory.build(), COMMENT_NEW, 'post_save' 
        )
        
        self.assertTrue(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_comment_changed_observer_added_for_major_changes_notification_level(self, observed_item):
        settings = create_fake_settings(
             notification_level=FEEDBACK_MAJOR_CHANGES
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, FeedbackFactory.build(), COMMENT_CHANGE, 'post_save' 
        )
        
        self.assertTrue(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_observe_feedback_changes_with_decision_creates_decision_change_observation(self, observed_item):
        settings = create_fake_settings()
        decision = DecisionFactory.build()
        settings_handler = ObservationManager()
        settings_handler._observe_feedback_changes(settings.user, decision, 
            "post_save")
        
        self.assertEqual(len(observed_item.call_args_list), 1)
        # observed_item.call_args_list is a tuple of tuples. We want to examine
        # the first element of the first call in the tuple, which is the list
        # of arguments the mock method was called with
        self.assertIn(DECISION_CHANGE, observed_item.call_args_list[0][0])
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_observe_feedback_changes_with_feedback_creates_feedback_new_observation(self, observed_item):
        settings = create_fake_settings()
        feedback = FeedbackFactory.build()
        settings_handler = ObservationManager()
        settings_handler._observe_feedback_changes(settings.user, feedback, 
           "post_save")
        
        self.assertEqual(len(observed_item.call_args_list), 1)
        # observed_item.call_args_list is a tuple of tuples. We want to examine
        # the first element of the first call in the tuple, which is the list
        # of arguments the mock method was called with
        self.assertIn(FEEDBACK_NEW, observed_item.call_args_list[0][0])
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_observe_major_feedback_changes_with_feedback_creates_feedback_change_observation(self, observed_item):
        settings = create_fake_settings()
        feedback = FeedbackFactory.build()
        settings_handler = ObservationManager()
        settings_handler._observe_major_feedback_changes(settings.user, 
           feedback, "post_save")
        
        self.assertEqual(len(observed_item.call_args_list), 1)
        # observed_item.call_args_list is a tuple of tuples. We want to examine
        # the first element of the first call in the tuple, which is the list
        # of arguments the mock method was called with
        self.assertIn(FEEDBACK_CHANGE, observed_item.call_args_list[0][0])
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_observe_major_feedback_changes_with_comment_creates_comment_new_observation(self, observed_item):
        settings = create_fake_settings()
        comment = CommentFactory.build()
        settings_handler = ObservationManager()
        settings_handler._observe_major_feedback_changes(settings.user, comment, 
           "post_save")
        
        self.assertEqual(len(observed_item.call_args_list), 2)
        # observed_item.call_args_list is a tuple of tuples. We want to examine
        # the first element of the first call in the tuple, which is the list
        # of arguments the mock method was called with
        self.assertIn(COMMENT_NEW, observed_item.call_args_list[0][0])
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_observe_major_feedback_changes_with_comment_creates_comment_change_observation(self, observed_item):
        settings = create_fake_settings()
        comment = CommentFactory.build()
        settings_handler = ObservationManager()
        settings_handler._observe_major_feedback_changes(settings.user, comment, 
           "post_save")
        
        self.assertEqual(len(observed_item.call_args_list), 2)
        # observed_item.call_args_list is a tuple of tuples. We want to examine
        # the first element of the second call in the tuple, which is the list
        # of arguments the mock method was called with
        self.assertIn(COMMENT_CHANGE, observed_item.call_args_list[1][0])
    
    @patch('publicweb.observation_manager.NotificationSettings.objects', 
           new=MagicMock(spec=NotificationSettings.objects, 
                get_or_create=(
                    lambda **kwargs: (NotificationSettings(**kwargs), True)
                )
           )
    )
    def test_get_settings_returns_settings_for_user(self):
        settings_handler = ObservationManager()
        user = UserFactory.build(id=1)
        settings = settings_handler.get_settings(
              user=user, 
              organization=OrganizationFactory.build()
        )
        self.assertEqual(user, settings.user)
    
    @patch('publicweb.observation_manager.NotificationSettings.objects', 
           new=MagicMock(spec=NotificationSettings.objects, 
                get_or_create=(
                    lambda **kwargs: (NotificationSettings(**kwargs), True)
                )
           )
    )
    def test_get_settings_returns_settings_for_organization(self):
        settings_handler = ObservationManager()
        organization = OrganizationFactory.build(id=2)
        settings = settings_handler.get_settings(
              user=UserFactory.build(), 
              organization=organization
        )
        self.assertEqual(organization, settings.organization)
    
    @patch('publicweb.observation_manager.NotificationSettings.objects', 
           new=MagicMock(spec=NotificationSettings.objects, 
                get_or_create=(
                    lambda **kwargs: (NotificationSettings(**kwargs), True)
                )
           )
    )
    def test_get_settings_notification_level_deault_is_main_items_only(self):
        settings_handler = ObservationManager()
        settings = settings_handler.get_settings(
              user=UserFactory.build(), 
              organization=OrganizationFactory.build()
        )
        self.assertEqual(
             MAIN_ITEMS_NOTIFICATIONS_ONLY, settings.notification_level
        )