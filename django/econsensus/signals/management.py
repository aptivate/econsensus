from django.conf import settings
from django.utils.translation import ugettext_noop as _
from django.db.models import signals
from django.contrib.auth.models import Permission
from django.contrib.auth import models as auth
from django.contrib.contenttypes.models import ContentType
from organizations.models import Organization

def create_org_editor_perm(app, created_models, verbosity, **kwargs):
    ct_organization = ContentType.objects.get_for_model(Organization)
    Permission.objects.create(codename='edit_decisions_feedback',
                              name='Can Add & Edit Decisions and Feedback',
                              content_type=ct_organization)

signals.post_syncdb.connect(create_org_editor_perm, sender=auth)

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
            "comment_new", 
            _("New Comment"), 
            _("New comment has been created."))
        
        notification.create_notice_type(
            "decision_change", 
            _("Decision Change"),
            _("There has been a change to a decision."))
        
        notification.create_notice_type(
            "feedback_change", 
            _("Feedback Change"), 
            _("There has been a change to feedback."))    
        
        notification.create_notice_type(
            "comment_change", 
            _("Comment Change"), 
            _("There has been a change to comment."))    

    signals.post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Skipping creation of NoticeTypes as notification app not found"


