from notification.models import observe
from publicweb.models import NO_NOTIFICATIONS, NotificationSettings,\
    MAIN_ITEMS_NOTIFICATIONS_ONLY, FEEDBACK_MAJOR_CHANGES,\
    FEEDBACK_ADDED_NOTIFICATIONS
from signals.management import DECISION_NEW, DECISION_STATUS_CHANGE,\
    FEEDBACK_CHANGE, DECISION_CHANGE, FEEDBACK_NEW, COMMENT_NEW, COMMENT_CHANGE

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
        return (notification_type == DECISION_CHANGE or 
                notification_type == FEEDBACK_NEW)
    
    def _notification_is_for_feedback_change(self, notification_type):
        return (notification_type == FEEDBACK_CHANGE or
                notification_type == COMMENT_NEW or
                notification_type == COMMENT_CHANGE)
    
    def _observe_basic_decision_changes(self, user, item, notification_type, signal):
        self._add_observeration(item, user, DECISION_NEW, signal)
        self._add_observeration(item, user, DECISION_STATUS_CHANGE, signal)
    
    def _observe_feedback_changes(self, user, item, notification_type, signal):
        self._add_observeration(item, user, DECISION_CHANGE, signal)
        self._add_observeration(item, user, FEEDBACK_NEW, signal)
    
    def _observe_major_feedback_changes(self, user, item, notification_type, signal):
        self._add_observeration(user, item, FEEDBACK_CHANGE, signal)
        self._add_observeration(user, item, COMMENT_NEW, signal)
        self._add_observeration(user, item, COMMENT_CHANGE, signal)
    
    def update_observers(self, settings, item, notification_type, signal):
        if (settings.notification_level > NO_NOTIFICATIONS and 
                self._notification_is_for_main_items(notification_type)):
            self._observe_basic_decision_changes(settings.user, 
                 item, notification_type, signal)
            
        if (settings.notification_level > MAIN_ITEMS_NOTIFICATIONS_ONLY and
                self._notification_is_for_feedback_creation(notification_type)):
            self._observe_feedback_changes(
                item, settings.user, notification_type, signal)
            
        if (settings.notification_level > FEEDBACK_ADDED_NOTIFICATIONS and
                self._notification_is_for_feedback_change(notification_type)):
            self._observe_major_feedback_changes(
                item, settings.user, notification_type, signal)
            
        if(settings.notification_level > FEEDBACK_MAJOR_CHANGES):
            self._add_observeration(
                item, settings.user, notification_type, signal)

        
            