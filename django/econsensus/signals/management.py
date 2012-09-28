from django.conf import settings
from django.utils.translation import ugettext_noop as _
from django.db.models import signals

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type(
            "decision_new", 
            _("New Decision"),
            _("A new decision has been created."))
        
        notification.create_notice_type(
            "feedback_new", 
            _("New Feedback"), 
            _("New feedback has been created."))

        notification.create_notice_type(
            "decision_change", 
            _("Decision Change"),
            _("There has been a change to a decision."))
        
        notification.create_notice_type(
            "feedback_change", 
            _("Feedback Change"), 
            _("There has been a change to feedback."))        

    signals.post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Skipping creation of NoticeTypes as notification app not found"

