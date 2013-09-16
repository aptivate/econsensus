from notification.models import observe
from publicweb.models import NO_NOTIFICATIONS, NotificationSettings,\
    MAIN_ITEMS_NOTIFICATIONS_ONLY
from signals.management import DECISION_NEW, DECISION_STATUS_CHANGE,\
    FEEDBACK_CHANGE, DECISION_CHANGE, FEEDBACK_NEW

class ObservationManager(object):
        
    def _add_observeration(self):
        pass
    
    def load_settings(self, user, organization):
        self.settings, _ = NotificationSettings.objects.get_or_create(
              user=user, organization=organization
        )
    
    def _notification_is_for_main_items(self, notification_type):
        return (notification_type == DECISION_NEW or 
                notification_type == DECISION_STATUS_CHANGE)
    
    def _notification_is_for_feedback_creation(self, notification_type):
        return notification_type == FEEDBACK_NEW
    
    def _observe_basic_decision_changes(self, item, notification_type, signal):
        self._add_observeration(item, self.settings.user, DECISION_NEW, signal)
        self._add_observeration(
            item, self.settings.user, DECISION_STATUS_CHANGE, signal)
        
    def update_watchers(self, item, notification_type, signal):
        if (self.settings.notification_level > NO_NOTIFICATIONS and 
                self._notification_is_for_main_items(notification_type)):
            self._observe_basic_decision_changes(item, notification_type, signal)
        if (self.settings.notification_level > MAIN_ITEMS_NOTIFICATIONS_ONLY and
                self._notification_is_for_feedback_creation(notification_type)):
            self._add_observeration(
                item, self.settings.user, notification_type, signal)
        
            