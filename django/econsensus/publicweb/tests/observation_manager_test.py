from django.test.testcases import SimpleTestCase
from publicweb.tests.factories import (NotificationSettingsFactory,
    DecisionFactory, FeedbackFactory)
from publicweb.models import NO_NOTIFICATIONS, MAIN_ITEMS_NOTIFICATIONS_ONLY,\
    FEEDBACK_ADDED_NOTIFICATIONS
from mock import patch
from publicweb.observation_manager import ObservationManager
from signals.management import (DECISION_STATUS_CHANGE, FEEDBACK_CHANGE, 
    DECISION_NEW, FEEDBACK_NEW)

def create_fake_settings(**kwargs):
    return NotificationSettingsFactory.build(
             notification_level=NO_NOTIFICATIONS
        )

class ObservationManagerTest(SimpleTestCase):
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_observer_not_created_for_no_notifications_level(self, observed_item):
        settings = create_fake_settings()
        settings_handler = ObservationManager()
        settings_handler.settings = settings

        settings_handler.update_watchers(
             DecisionFactory.build(), DECISION_NEW, 'post_save' 
        )
        
        self.assertFalse(observed_item.called)

    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_new_decision_observer_created_for_main_items_notification_level(self, observed_item):
        settings = NotificationSettingsFactory.build(
             notification_level=MAIN_ITEMS_NOTIFICATIONS_ONLY
        )
        
        settings_handler = ObservationManager()
        settings_handler.settings = settings
        settings_handler.update_watchers(
             DecisionFactory.build(), DECISION_NEW, 'post_save' 
        )
        
        self.assertTrue(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_decision_status_change_observer_created_for_main_items_notification_level(self, observed_item):
        settings = NotificationSettingsFactory.build(
             notification_level=MAIN_ITEMS_NOTIFICATIONS_ONLY
        )
        
        settings_handler = ObservationManager()
        settings_handler.settings = settings
        settings_handler.update_watchers(
             DecisionFactory.build(), DECISION_STATUS_CHANGE, 'post_save' 
        )
        
        self.assertTrue(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_feedback_created_observer_not_created_for_main_items_notification_level(self, observed_item):
        settings = NotificationSettingsFactory.build(
             notification_level=MAIN_ITEMS_NOTIFICATIONS_ONLY
        )
        
        settings_handler = ObservationManager()
        settings_handler.settings = settings
        settings_handler.update_watchers(
             FeedbackFactory.build(), FEEDBACK_NEW, 'post_save' 
        )
        
        self.assertFalse(observed_item.called)
    
    @patch('publicweb.observation_manager.ObservationManager._add_observeration')
    def test_feedback_created_observer_created_for_feedback_added_notification_level(self, observed_item):
        settings = NotificationSettingsFactory.build(
             notification_level=FEEDBACK_ADDED_NOTIFICATIONS
        )
        
        settings_handler = ObservationManager()
        settings_handler.settings = settings
        settings_handler.update_watchers(
             FeedbackFactory.build(), FEEDBACK_NEW, 'post_save' 
        )
        
        self.assertTrue(observed_item.called)