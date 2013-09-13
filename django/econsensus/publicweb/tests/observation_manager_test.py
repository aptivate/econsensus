from django.test.testcases import SimpleTestCase
from publicweb.tests.factories import NotificationSettingsFactory,\
    DecisionFactory
from publicweb.models import NO_NOTIFICATIONS, MAIN_ITEMS_NOTIFICATIONS_ONLY
from mock import patch, MagicMock
from notification.models import ObservedItem
from publicweb.observation_manager import ObservationManager

class ObservationManagerTest(SimpleTestCase):
    @patch('publicweb.observation_manager.ObservedItem', return_value=MagicMock(spec=ObservedItem))
    def test_observer_not_created_for_user_with_no_notifications(self, observed_item):        
        settings = NotificationSettingsFactory.build(
             notification_level=NO_NOTIFICATIONS
        )
        
        settings_handler = ObservationManager()
        settings_handler.update_watchers(
             DecisionFactory.build(), settings.user, 'decision_change' 
        )
        
        self.assertFalse(observed_item.return_value.save.called)
    