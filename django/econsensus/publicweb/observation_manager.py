from publicweb.models import (NO_NOTIFICATIONS, NotificationSettings,
    MAIN_ITEMS_NOTIFICATIONS_ONLY, FEEDBACK_ADDED_NOTIFICATIONS, 
    FEEDBACK_MAJOR_CHANGES)
from signals.management import (DECISION_NEW, DECISION_STATUS_CHANGE,
    FEEDBACK_CHANGE, DECISION_CHANGE, FEEDBACK_NEW, COMMENT_NEW, COMMENT_CHANGE,
    MINOR_CHANGE)

class ObservationManager(object):
    recipient_list = None
    
    def __init__(self):
        self.recipitant_list = set()
       
    def _add_observeration(self, user):
        self.recipitant_list.add(user)
    
    def get_settings(self, user, organization):
        settings, _ = NotificationSettings.objects.get_or_create(
              user=user, organization=organization
        )
        return settings
    
    def update_observers(self, settings, notification_type):
        notifications = {
             NO_NOTIFICATIONS: (DECISION_NEW, DECISION_STATUS_CHANGE),
             MAIN_ITEMS_NOTIFICATIONS_ONLY: (DECISION_CHANGE, FEEDBACK_NEW),
             FEEDBACK_ADDED_NOTIFICATIONS: (
                    FEEDBACK_CHANGE, COMMENT_NEW, COMMENT_CHANGE),
             FEEDBACK_MAJOR_CHANGES: (MINOR_CHANGE,)
             }
        for key, types in notifications.items():
            if settings.notification_level > key and notification_type in types:
                self._add_observeration(settings.user) 
