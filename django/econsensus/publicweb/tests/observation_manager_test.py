from django.test.testcases import SimpleTestCase
from publicweb.tests.factories import (NotificationSettingsFactory,
    DecisionFactory, FeedbackFactory, CommentFactory, UserFactory,
    OrganizationFactory)
from publicweb.models import (NO_NOTIFICATIONS, MAIN_ITEMS_NOTIFICATIONS_ONLY,
    FEEDBACK_ADDED_NOTIFICATIONS, FEEDBACK_MAJOR_CHANGES, NotificationSettings,
    MINOR_CHANGES_NOTIFICATIONS)
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
             settings, DECISION_NEW 
        )
        
        self.assertFalse(observed_item.called)

    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_new_decision_observer_created_for_main_items_notification_level(self, observed_item):
        settings = create_fake_settings(
            notification_level=MAIN_ITEMS_NOTIFICATIONS_ONLY
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, DECISION_NEW 
        )
        
        self.assertTrue(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_decision_status_change_observer_created_for_main_items_notification_level(self, observed_item):
        settings = create_fake_settings(
             notification_level=MAIN_ITEMS_NOTIFICATIONS_ONLY
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, DECISION_STATUS_CHANGE, 
        )
        
        self.assertTrue(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_decision_change_observer_not_created_for_main_items_notification_level(self, observed_item):
        settings = create_fake_settings(
            notification_level=MAIN_ITEMS_NOTIFICATIONS_ONLY
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers( 
            settings, DECISION_CHANGE 
        )
        
        self.assertFalse(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_feedback_created_observer_not_created_for_main_items_notification_level(self, observed_item):
        settings = create_fake_settings(
             notification_level=MAIN_ITEMS_NOTIFICATIONS_ONLY
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers( 
             settings, FEEDBACK_NEW 
        )
        
        self.assertFalse(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_decision_changed_observer_created_for_feedback_added_level(self, observed_item):
        settings = create_fake_settings(
            notification_level=FEEDBACK_ADDED_NOTIFICATIONS
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers( 
            settings, DECISION_CHANGE
        )
        
        self.assertTrue(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_feedback_created_observer_created_for_feedback_added_notification_level(self, observed_item):
        settings = create_fake_settings(
             notification_level=FEEDBACK_ADDED_NOTIFICATIONS
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, FEEDBACK_NEW 
        )
        
        self.assertTrue(observed_item.called)
        
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_feedback_changed_observer_not_added_for_feedback_added_notification_level(self, observed_item):
        settings = create_fake_settings(
             notification_level=FEEDBACK_ADDED_NOTIFICATIONS
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, FEEDBACK_CHANGE 
        )
        
        self.assertFalse(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_feedback_changed_observer_added_for_major_changes_notification_level(self, observed_item):
        settings = create_fake_settings(
             notification_level=FEEDBACK_MAJOR_CHANGES
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, FEEDBACK_CHANGE 
        )
        
        self.assertTrue(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_minor_change_observer_not_added_for_major_changes_notification_level(self, observed_item):
        settings = create_fake_settings(
             notification_level=FEEDBACK_MAJOR_CHANGES
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, MINOR_CHANGE
        )
        
        self.assertFalse(observed_item.called)
        
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_comment_created_observer_added_for_major_changes_notification_level(self, observed_item):
        settings = create_fake_settings(
             notification_level=FEEDBACK_MAJOR_CHANGES
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, COMMENT_NEW
        )
        
        self.assertTrue(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_comment_changed_observer_added_for_major_changes_notification_level(self, observed_item):
        settings = create_fake_settings(
             notification_level=FEEDBACK_MAJOR_CHANGES
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, COMMENT_CHANGE 
        )
        
        self.assertTrue(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_minor_change_observer_added_for_minor_changes_notification_level(self, observed_item):
        settings = NotificationSettingsFactory.build(
             notification_level=MINOR_CHANGES_NOTIFICATIONS
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, MINOR_CHANGE
        )
        
        self.assertTrue(observed_item.called)    
        
    
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
