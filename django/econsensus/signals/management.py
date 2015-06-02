from django.conf import settings
from django.utils.translation import ugettext_noop as _
from django.db.models import signals
from django.contrib.auth.models import Permission
from django.contrib.auth import models as auth
from django.contrib.contenttypes.models import ContentType
from organizations.models import Organization

def create_org_editor_perm(app, created_models, verbosity, **kwargs):
    ct_organization = ContentType.objects.get_for_model(Organization)
    Permission.objects.get_or_create(codename='edit_decisions_feedback',
                              name='Can Add & Edit Decisions and Feedback',
                              content_type=ct_organization)


signals.post_syncdb.connect(create_org_editor_perm, sender=auth)


DECISION_NEW = "decision_new"
FEEDBACK_NEW = "feedback_new"
ACTIONITEM_NEW = "action_item_new"
COMMENT_NEW = "comment_new"
DECISION_CHANGE = "decision_change"
FEEDBACK_CHANGE = "feedback_change"
ACTIONITEM_CHANGE = "action_item_change"
COMMENT_CHANGE = "comment_change"
DECISION_STATUS_CHANGE = "decision_status_change"
MINOR_CHANGE = "minor_change"


if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type(
            DECISION_NEW,
            _("New Decision"),
            _("A new decision has been created."))

        notification.create_notice_type(
            FEEDBACK_NEW,
            _("New Feedback"),
            _("New feedback has been created."))

        notification.create_notice_type(
            ACTIONITEM_NEW,
            _("New Action Item"),
            _("An action item has been created."))

        notification.create_notice_type(
            COMMENT_NEW,
            _("New Comment"),
            _("New comment has been created."))

        notification.create_notice_type(
            DECISION_CHANGE,
            _("Decision Change"),
            _("There has been a change to a decision."))

        notification.create_notice_type(
            FEEDBACK_CHANGE,
            _("Feedback Change"),
            _("There has been a change to feedback."))

        notification.create_notice_type(
            ACTIONITEM_CHANGE,
            _("Action Item Change"),
            _("There has been a change to action item."))

        notification.create_notice_type(
            COMMENT_CHANGE,
            _("Comment Change"),
            _("There has been a change to comment."))

        notification.create_notice_type(
            DECISION_STATUS_CHANGE,
            _("Decision Change"),
            _("There has been a change to decision's type."))

        notification.create_notice_type(
            MINOR_CHANGE,
            _("Minor Change"),
            _("There has been a change that was marked as minor."))

    signals.post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Skipping creation of NoticeTypes as notification app not found"


