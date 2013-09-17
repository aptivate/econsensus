from notification.models import observe
from publicweb.models import (NO_NOTIFICATIONS, NotificationSettings,
    MAIN_ITEMS_NOTIFICATIONS_ONLY, FEEDBACK_ADDED_NOTIFICATIONS, Decision, 
    Feedback)
from signals.management import (DECISION_NEW, DECISION_STATUS_CHANGE,
    FEEDBACK_CHANGE, DECISION_CHANGE, FEEDBACK_NEW, COMMENT_NEW, COMMENT_CHANGE)

class ObservationManager(object):
        
    def _add_observeration(self, observed, observer, notice_type, signal):
        observe(observed, observer, notice_type, signal)
    
    def get_settings(self, user, organization):
        settings, _ = NotificationSettings.objects.get_or_create(
              user=user, organization=organization
        )
        return settings
    
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
    
    def _observe_basic_decision_changes(self, user, item, signal):
        self._add_observeration(item, user, DECISION_NEW, signal)
        self._add_observeration(item, user, DECISION_STATUS_CHANGE, signal)
    
    def _observe_feedback_changes(self, user, item, signal):
        if isinstance(item, Decision):
            self._add_observeration(item, user, DECISION_CHANGE, signal)
        else:
            self._add_observeration(item, user, FEEDBACK_NEW, signal)
    
    def _observe_major_feedback_changes(self, user, item, signal):
        if isinstance(item, Feedback):
            self._add_observeration(user, item, FEEDBACK_CHANGE, signal)
        else:
            self._add_observeration(user, item, COMMENT_NEW, signal)
            self._add_observeration(user, item, COMMENT_CHANGE, signal)
    
    def update_observers(self, settings, item, notification_type, signal):
        if (settings.notification_level > NO_NOTIFICATIONS and 
                self._notification_is_for_main_items(notification_type)):
            self._observe_basic_decision_changes(settings.user, item, signal)
            
        if (settings.notification_level > MAIN_ITEMS_NOTIFICATIONS_ONLY and
                self._notification_is_for_feedback_creation(notification_type)):
            self._observe_feedback_changes(item, settings.user, signal)
            
        if (settings.notification_level > FEEDBACK_ADDED_NOTIFICATIONS and
                self._notification_is_for_feedback_change(notification_type)):
            self._observe_major_feedback_changes(item, settings.user, signal)
        
        # The minor changes setting doesn't relate to any specific item so we 
        # don't add an observation for it.
            