from publicweb.models import (NO_NOTIFICATIONS, NotificationSettings,
    MAIN_ITEMS_NOTIFICATIONS_ONLY, FEEDBACK_ADDED_NOTIFICATIONS, 
    FEEDBACK_MAJOR_CHANGES, Feedback)
from signals.management import (DECISION_NEW, DECISION_STATUS_CHANGE,
    FEEDBACK_CHANGE, DECISION_CHANGE, FEEDBACK_NEW, COMMENT_NEW, COMMENT_CHANGE,
    MINOR_CHANGE)
from django.contrib.comments.models import Comment

class ObservationManager(object):
    recipient_list = None
    
    def __init__(self):
        self.recipient_list = set()
    
    def _get_decision(self, item):
        if isinstance(item, Comment):
            item = item.content_object
        if isinstance(item, Feedback):
            item = item.decision
        return item
       
    def _add_recipient(self, user):
        self.recipient_list.add(user)#
        
    def _get_organization(self, item):
        item = self._get_decision(item)
        return item.organization
    
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
                    FEEDBACK_CHANGE, COMMENT_NEW, COMMENT_CHANGE
             ),
             FEEDBACK_MAJOR_CHANGES: (MINOR_CHANGE,)
        }
        for key, types in notifications.items():
            if settings.notification_level > key and notification_type in types:
                self._add_recipient(settings.user)
    
    def include_watchers(self, item):
        item = self._get_decision(item)
        self.recipient_list.update(
            [watcher.user for watcher in item.watchers.all()]
        )        
