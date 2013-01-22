#pylint: disable=E1102
#config import is unused but required here for livesettings
import config #pylint: disable=W0611
import re

from notification import models as notification

from django.db import models
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.contenttypes import generic
from django.dispatch import receiver
from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models import Count

from tagging.fields import TagField
from organizations.models import Organization
from managers import DecisionManager

# Ideally django-tinymce should be patched
# http://south.aeracode.org/wiki/MyFieldsDontWork
# http://code.google.com/p/django-tinymce/issues/detail?id=80
# TODO: Status codes could possibly be harvested off into its
# own class with accessor methods to return values.

from south.modelsinspector import add_introspection_rules

add_introspection_rules([], ["^tagging\.fields\.TagField"])

class Decision(models.Model):

    TAGS_HELP_FIELD_TEXT = "Enter a list of tags separated by spaces."
    DISCUSSION_STATUS = 'discussion'
    PROPOSAL_STATUS = 'proposal'
    DECISION_STATUS = 'decision'
    ARCHIVED_STATUS = 'archived'

    STATUS_CHOICES = (
                  (DISCUSSION_STATUS, _('discussion')),
                  (PROPOSAL_STATUS, _('proposal')),
                  (DECISION_STATUS, _('decision')),
                  (ARCHIVED_STATUS, _('archived')),
                  )

    DEFAULT_SIZE = 140

    #User entered fields
    description = models.TextField(verbose_name=_('Description'))
    decided_date = models.DateField(null=True, blank=True,
        verbose_name=_('Decided Date'))
    effective_date = models.DateField(null=True, blank=True,
        verbose_name=_('Effective Date'))
    review_date = models.DateField(null=True, blank=True,
        verbose_name=_('Review Date'))
    expiry_date = models.DateField(null=True, blank=True,
        verbose_name=_('Expiry Date'))
    deadline = models.DateField(null=True, blank=True,
        verbose_name=_('Deadline'))
    archived_date = models.DateField(null=True, blank=True,
        verbose_name=_('Archived Date'))
    budget = models.CharField(blank=True, max_length=255,
        verbose_name=_('Budget/Resources'))
    people = models.CharField(max_length=255, null=True, blank=True)
    meeting_people = models.CharField(max_length=255, null=True, blank=True)    
    status = models.CharField(choices=STATUS_CHOICES,
                                 default=PROPOSAL_STATUS,
                                 max_length=10)
    tags = TagField(null=True, blank=True, editable=True, 
                    help_text=TAGS_HELP_FIELD_TEXT)
    organization = models.ForeignKey(Organization)
    #admin stuff
    author = models.ForeignKey(User, blank=True, null=True, editable=False, related_name="%(app_label)s_%(class)s_authored")
    editor = models.ForeignKey(User, blank=True, null=True, editable=False, related_name="%(app_label)s_%(class)s_edited")
    last_modified = models.DateTimeField(null=True, auto_now=True, verbose_name=_('Last Modified'))
    last_status = models.CharField(choices=STATUS_CHOICES,
                                 default="new",
                                 max_length=10, editable=False)

    watchers = generic.GenericRelation(notification.ObservedItem)

    #Autocompleted fields
    #should use editable=False?
    excerpt = models.CharField(verbose_name=_('Excerpt'), max_length=255, blank=True)
    creation = models.DateField(null=True, auto_now_add=True,
        verbose_name=_('Creation'))

    objects = DecisionManager()

    #methods
    def unresolvedfeedback(self):
        answer = _("No")
        linked_feedback = self.feedback_set.all()
        for thisfeedback in linked_feedback:
            if (not thisfeedback.resolved):

                answer = _("Yes")
                break
            
        return answer

    unresolvedfeedback.short_description = _("Unresolved Feedback")

    def feedbackcount(self):
        return self.feedback_set.all().count()    

    feedbackcount.short_description = _("Feedback")

    def _get_excerpt(self):
        description = strip_tags(self.description)
        match = re.search("\.|\\r|\\n", description)
        position = self.DEFAULT_SIZE
        if match:
            start = match.start()
            if start < position:
                position = start
        return description[:position]
    
    def __unicode__(self):
        return self.excerpt

    @classmethod
    def get_fields(cls):
        return cls._meta.fields
    
    @models.permalink
    def get_absolute_url(self):
        return ('publicweb_item_detail', [self.id])
    
    def get_email(self):
        """
        Generates an email address based on the Decision's organization
        and settings.DEFAULT_FROM_EMAIL
        """
        default_from_email = settings.DEFAULT_FROM_EMAIL
        return re.sub('\w+@', "%s@" % self.organization.slug, default_from_email)
    
    def get_feedback_statistics(self):
        statistics = dict([(unicode(x),0) for x in Feedback.rating_names])
        raw_data = self.feedback_set.values('rating').annotate(Count('rating'))
        for x in raw_data:
            key = unicode(Feedback.rating_names[x['rating']])
            statistics[key] = x['rating__count']
        return statistics

    def get_message_id(self):
        """
        Generates a message id that can be used in email headers
        """
        return "decision-%s@%s" % (self.id, Site.objects.get_current().domain)

    def save(self, *args, **kwargs):
        self.excerpt = self._get_excerpt()
        super(Decision, self).save(*args, **kwargs)
        
class Feedback(models.Model):

    rating_names = (_('question'), _('danger'), _('concerns'), _('consent'), _('comment'))

    RATING_CHOICES = [(rating_names.index(x), x) for x in rating_names]
    
    QUESTION_STATUS = rating_names.index('question')
    DANGER_STATUS = rating_names.index('danger')
    CONCERNS_STATUS = rating_names.index('concerns')
    CONSENT_STATUS = rating_names.index('consent')
    COMMENT_STATUS = rating_names.index('comment')
    
    description = models.TextField(verbose_name=_('Description'), null=True, blank=True)
    author = models.ForeignKey(User, blank=True, null=True, editable=False, related_name="%(app_label)s_%(class)s_related")
    editor = models.ForeignKey(User, blank=True, null=True, editable=False, related_name="%(app_label)s_%(class)s_edited")
    decision = models.ForeignKey('Decision', verbose_name=_('Decision'))
    resolved = models.BooleanField(verbose_name=_('Resolved'))
    rating = models.IntegerField(choices=RATING_CHOICES, default=COMMENT_STATUS)

    @models.permalink
    def get_absolute_url(self):
        return ('publicweb_feedback_detail', [self.id])

    @models.permalink
    def get_parent_url(self):
        return ('publicweb_item_detail', [self.decision.id])
    
    def get_author_name(self):
        if hasattr(self.author, 'get_full_name') and self.author.get_full_name():
            return self.author.get_full_name()
        elif hasattr(self.author, 'username') and self.author.username:
            return self.author.username
        else:
            return "An Anonymous Contributor"

    def get_message_id(self):
        """
        Generates a message id that can be used in email headers
        """
        return "feedback-%s@%s" % (self.id, Site.objects.get_current().domain)

if notification is not None:
    @receiver(models.signals.post_save, sender=Decision, dispatch_uid="publicweb.models.decision_signal_handler")
    def decision_signal_handler(sender, **kwargs):
        """
        All users except the author will get a notification informing them of 
        new content.
        All users are made observers of the decision.
        Notices are sent for observed decisions when feedback changes.
        """
        instance = kwargs.get('instance')
        headers = {'Message-ID' : instance.get_message_id()}

        if kwargs.get('created', True):
            all_users = instance.organization.users.all()
            all_but_author = all_users.exclude(username=instance.author)
            for user in all_users:
                notification.observe(instance, user, 'decision_change')
            extra_context = {}
            extra_context.update({"observed": instance})
            notification.send(all_but_author, "decision_new", extra_context, headers, from_email=instance.get_email())
        else:
            notification.send_observation_notices_for(instance, headers=headers)
            
    @receiver(models.signals.post_save, sender=Feedback, dispatch_uid="publicweb.models.feedback_signal_handler")
    def feedback_signal_handler(sender, **kwargs):
        """
        All watchers of a decision will get a notification informing them of
        new feedback.
        All watchers become observers of the feedback.
        """
        instance = kwargs.get('instance')
        headers = {'Message-ID' : instance.get_message_id()}
        headers.update({'In-Reply-To' : instance.decision.get_message_id()})        
        
        if kwargs.get('created', True):
            #author gets notified if the feedback is edited.
            notification.observe(instance, instance.author, 'feedback_change')

            #All watchers of parent get notified of new feedback.
            all_observed_items_but_authors = list(instance.decision.watchers.exclude(user=instance.author))
            observer_list = [x.user for x in all_observed_items_but_authors]
            extra_context = dict({"observed": instance})
            notification.send(observer_list, "feedback_new", extra_context, headers, from_email=instance.decision.get_email())
        else:
            if instance.author != instance.editor:
                notification.send_observation_notices_for(instance, headers=headers)
            
            
    @receiver(models.signals.post_save, sender=Comment, dispatch_uid="publicweb.models.comment_signal_handler")
    def comment_signal_handler(sender, **kwargs):
        """
        All watchers of a decision will get a notification informing them of
        new comment.
        All watchers become observers of the comment.
        """
        instance = kwargs.get('instance')
        headers = {'Message-ID' : "comment-%s@%s" % (instance.id, Site.objects.get_current().domain)}
        headers.update({'In-Reply-To' : instance.content_object.get_message_id()})        
        
        if kwargs.get('created', True):
            # Creator gets notified if the comment is edited.
            notification.observe(instance, instance.user, 'comment_change')

            #All watchers of parent get notified of new comment.
            all_observed_items_but_author = list(instance.content_object.decision.watchers.exclude(user=instance.user))
            observer_list = [x.user for x in all_observed_items_but_author]
            extra_context = dict({"observed": instance})
            notification.send(observer_list, "comment_new", extra_context, headers, from_email=instance.content_object.decision.get_email())
        else:
            notification.send_observation_notices_for(instance, headers=headers)
            
