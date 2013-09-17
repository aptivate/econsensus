from django.test.testcases import SimpleTestCase
from publicweb.tests.factories import (NotificationSettingsFactory,
    DecisionFactory, FeedbackFactory)
from publicweb.models import NO_NOTIFICATIONS, MAIN_ITEMS_NOTIFICATIONS_ONLY,\
    FEEDBACK_ADDED_NOTIFICATIONS, FEEDBACK_MAJOR_CHANGES,\
    MINOR_CHANGES_NOTIFICATIONS
from mock import patch
from publicweb.observation_manager import ObservationManager
from signals.management import (DECISION_STATUS_CHANGE, FEEDBACK_CHANGE, 
    DECISION_NEW, FEEDBACK_NEW, DECISION_CHANGE, COMMENT_NEW, COMMENT_CHANGE,
    MINOR_CHANGE)

def create_fake_settings(**kwargs):
    return NotificationSettingsFactory.build(
             notification_level=NO_NOTIFICATIONS
        )

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
        settings = NotificationSettingsFactory.build(
             notification_level=MAIN_ITEMS_NOTIFICATIONS_ONLY
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, DecisionFactory.build(), DECISION_NEW, 'post_save' 
        )
        
        self.assertTrue(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_decision_status_change_observer_created_for_main_items_notification_level(self, observed_item):
        settings = NotificationSettingsFactory.build(
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
        settings = NotificationSettingsFactory.build(
            notification_level=MAIN_ITEMS_NOTIFICATIONS_ONLY
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers( 
            settings, DecisionFactory.build(), DECISION_CHANGE, 'post_save' 
        )
        
        self.assertFalse(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_feedback_created_observer_not_created_for_main_items_notification_level(self, observed_item):
        settings = NotificationSettingsFactory.build(
             notification_level=MAIN_ITEMS_NOTIFICATIONS_ONLY
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers( 
             settings, FeedbackFactory.build(), FEEDBACK_NEW, 'post_save' 
        )
        
        self.assertFalse(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_decision_changed_observer_created_for_feedback_added_level(self, observed_item):
        settings = NotificationSettingsFactory.build(
            notification_level=FEEDBACK_ADDED_NOTIFICATIONS
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers( 
            settings, DecisionFactory.build(), DECISION_CHANGE, 'post_save' 
        )
        
        self.assertTrue(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_feedback_created_observer_created_for_feedback_added_notification_level(self, observed_item):
        settings = NotificationSettingsFactory.build(
             notification_level=FEEDBACK_ADDED_NOTIFICATIONS
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, FeedbackFactory.build(), FEEDBACK_NEW, 'post_save' 
        )
        
        self.assertTrue(observed_item.called)
        
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_feedback_changed_observer_not_added_for_feedback_added_notification_level(self, observed_item):
        settings = NotificationSettingsFactory.build(
             notification_level=FEEDBACK_ADDED_NOTIFICATIONS
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, FeedbackFactory.build(), FEEDBACK_CHANGE, 'post_save' 
        )
        
        self.assertFalse(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_feedback_changed_observer_added_for_major_changes_notification_level(self, observed_item):
        settings = NotificationSettingsFactory.build(
             notification_level=FEEDBACK_MAJOR_CHANGES
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, FeedbackFactory.build(), FEEDBACK_CHANGE, 'post_save' 
        )
        
        self.assertTrue(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_minor_change_observer_not_added_for_major_changes_notification_level(self, observed_item):
        settings = NotificationSettingsFactory.build(
             notification_level=FEEDBACK_MAJOR_CHANGES
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, FeedbackFactory.build(), MINOR_CHANGE, 'post_save' 
        )
        
        self.assertFalse(observed_item.called)
        
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_comment_created_observer_added_for_major_changes_notification_level(self, observed_item):
        settings = NotificationSettingsFactory.build(
             notification_level=FEEDBACK_MAJOR_CHANGES
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, FeedbackFactory.build(), COMMENT_NEW, 'post_save' 
        )
        
        self.assertTrue(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_comment_changed_observer_added_for_major_changes_notification_level(self, observed_item):
        settings = NotificationSettingsFactory.build(
             notification_level=FEEDBACK_MAJOR_CHANGES
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, FeedbackFactory.build(), COMMENT_CHANGE, 'post_save' 
        )
        
        self.assertTrue(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_minor_chage_observer_added_for_minor_changes_notification_level(self, observed_item):
        settings = NotificationSettingsFactory.build(
             notification_level=MINOR_CHANGES_NOTIFICATIONS
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_observers(
             settings, FeedbackFactory.build(), COMMENT_CHANGE, 'post_save' 
        )
        
        self.assertTrue(observed_item.called)    
        