#pylint: disable-msg=E1102

from django.db import models
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from tagging.fields import TagField
import datetime
from emails import OpenConsentEmailMessage
from managers import DecisionManager

import re

# Ideally django-tinymce should be patched
# http://south.aeracode.org/wiki/MyFieldsDontWork
# http://code.google.com/p/django-tinymce/issues/detail?id=80
# TODO: Status codes could possibly be harvested off into its
# own class with accessor methods to return values.

from south.modelsinspector import add_introspection_rules

add_introspection_rules([], ["^tagging\.fields\.TagField"])

class Decision(models.Model):

    TAGS_HELP_FIELD_TEXT = "Enter a list of tags separated by spaces."
    PROPOSAL_STATUS = 'proposal'
    DECISION_STATUS = 'decision'
    ARCHIVED_STATUS = 'archived'

    STATUS_CHOICES = (
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

    #admin stuff
    author = models.ForeignKey(User, blank=True, null=True, editable=False, related_name="%(app_label)s_%(class)s_authored")
    editor = models.ForeignKey(User, blank=True, null=True, editable=False, related_name="%(app_label)s_%(class)s_edited")
    last_modified = models.DateTimeField(null=True, auto_now=True, verbose_name=_('Last Modified'))
    
    watchers = models.ManyToManyField(User, blank=True, editable=False)
    
    #Autocompleted fields
    #should use editable=False?
    excerpt = models.CharField(verbose_name=_('Excerpt'), max_length=255, blank=True)
    creation = models.DateField(null=True, auto_now_add=True,
        verbose_name=_('Creation'))

    objects = DecisionManager()

    #methods
    def is_watched(self, user):
        return user in self.watchers.all()
                        
    def add_watcher(self, user):
        if user not in self.watchers.all():
            self.watchers.add(user)
    
    def remove_watcher(self, user):
        if user in self.watchers.all():
            self.watchers.remove(user)

    def watchercount(self):
        return self.watchers.count()

    watchercount.short_description = _("Watchers")

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
        return ('publicweb_item_detail', (), {'object_id':self.id})
    
    def get_feedback_statistics(self):
        statistics = {'all': 0,
                      'question': 0,
                      'danger': 0,
                      'concern': 0,
                      'comment': 0,
                      'consent': 0
                     }
        
        #is there a better way of doing this,
        #using object/filter/count? - pcb
        for feedback in self.feedback_set.all():
            if feedback.rating == Feedback.QUESTION_STATUS:
                statistics['question'] += 1
            elif feedback.rating == Feedback.DANGER_STATUS:
                statistics['danger'] += 1
            elif feedback.rating == Feedback.CONCERNS_STATUS:
                statistics['concern'] += 1
            elif feedback.rating == Feedback.COMMENT_STATUS:
                statistics['comment'] += 1
            elif feedback.rating == Feedback.CONSENT_STATUS:
                statistics['consent'] += 1
            statistics['all'] += 1
        
        return statistics

    def save(self, *args, **kwargs):
        self.excerpt = self._get_excerpt()       
        super(Decision, self).save(*args, **kwargs)
        
class Feedback(models.Model):

    QUESTION_STATUS = 0
    DANGER_STATUS = 1
    CONCERNS_STATUS = 2
    CONSENT_STATUS = 3
    COMMENT_STATUS = 4

    RATING_CHOICES = ( 
                  (QUESTION_STATUS, _('question')),
                  (DANGER_STATUS, _('danger')),
                  (CONCERNS_STATUS, _('concerns')),
                  (CONSENT_STATUS, _('consent')),
                  (COMMENT_STATUS, _('comment')),
                  )
    
    description = models.TextField(verbose_name=_('Description'), null=True, blank=True)
    author = models.ForeignKey(User, blank=True, null=True, editable=False, related_name="%(app_label)s_%(class)s_related")    
    decision = models.ForeignKey('Decision', verbose_name=_('Decision'))
    resolved = models.BooleanField(verbose_name=_('Resolved'))
    rating = models.IntegerField(choices=RATING_CHOICES, default=COMMENT_STATUS)

    @models.permalink
    def get_absolute_url(self):
        return ('publicweb_feedback_detail', (), {'object_id':self.id})

    @models.permalink
    def get_parent_url(self):
        return ('publicweb_item_detail', (), {'object_id': self.decision.id})
    
    def get_author_name(self):
        if hasattr(self.author, 'get_full_name') and self.author.get_full_name():
            return self.author.get_full_name()
        elif hasattr(self.author, 'username') and self.author.username:
            return self.author.username
        else:
            return "An Anonymous Contributor"

    def rating_text(self):
        return self.RATING_CHOICES[self.rating][1]
