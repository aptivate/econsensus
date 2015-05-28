"""
This file contains models that must be removed from the models.py file to prevent circular imports
"""
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from organizations.models import Organization

STANDARD_SENDING_HEADERS = {'Precedence': 'bulk', 'Auto-Submitted': 'auto-generated'}

# The indexes are numeric because the notification levels are cumulative
# This enables us to do if notification_level >= number
NO_NOTIFICATIONS = 0
NO_NOTIFICATIONS_TEXT = _("1. Silent")
MAIN_ITEMS_NOTIFICATIONS_ONLY = 1
MAIN_ITEMS_NOTIFICATIONS_ONLY_TEXT = _("2. Major events")
FEEDBACK_ADDED_NOTIFICATIONS = 2
FEEDBACK_ADDED_NOTIFICATIONS_TEXT = _("3. Feedback and changes")
FEEDBACK_MAJOR_CHANGES = 3
FEEDBACK_MAJOR_CHANGES_TEXT = _("4. Full discussion")
MINOR_CHANGES_NOTIFICATIONS = 4
MINOR_CHANGES_NOTIFICATIONS_TEXT = _("5. Everything, even minor changes")
NOTIFICATION_LEVELS = (
          (NO_NOTIFICATIONS, NO_NOTIFICATIONS_TEXT),
          (MAIN_ITEMS_NOTIFICATIONS_ONLY, MAIN_ITEMS_NOTIFICATIONS_ONLY_TEXT),
          (FEEDBACK_ADDED_NOTIFICATIONS, FEEDBACK_ADDED_NOTIFICATIONS_TEXT),
          (FEEDBACK_MAJOR_CHANGES, FEEDBACK_MAJOR_CHANGES_TEXT),
          (MINOR_CHANGES_NOTIFICATIONS, MINOR_CHANGES_NOTIFICATIONS_TEXT)
                      )


class NotificationSettings(models.Model):
    user = models.ForeignKey(User)
    organization = models.ForeignKey(Organization)
    notification_level = models.IntegerField(choices=NOTIFICATION_LEVELS,
        default=FEEDBACK_MAJOR_CHANGES,
        verbose_name=_("Notification level"),
        help_text=_("Levels are cumulative, so if, for example, you choose to "
            "get notifications of replies to feedback, you will get "
            "notifications of all changes to main items as well."))

    class Meta:
        unique_together = ('user', 'organization')

class OrganizationSettings(models.Model):
    organization = models.OneToOneField(Organization)
    default_notification_level = models.IntegerField(choices=NOTIFICATION_LEVELS,
        help_text=_("Levels are cumulative, so if, for example, you choose to "
            "get notifications of replies to feedback, you will get "
            "notifications of all changes to main items as well."))
