from django.db import models
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from tagging.fields import TagField

from emails import OpenConsentEmailMessage
import tinymce.models
import re

# Ideally django-tinymce should be patched
# http://south.aeracode.org/wiki/MyFieldsDontWork
# http://code.google.com/p/django-tinymce/issues/detail?id=80
from south.modelsinspector import add_introspection_rules

add_introspection_rules([], ["^tagging\.fields\.TagField"])


class Idea(models.Model):
    excerpt = models.CharField(max_length=255,
                                           blank=True)
    description = models.TextField(verbose_name=_('Description'))
    
    DEFAULT_SIZE = 140
    
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

    def save(self, *args, **kwargs):
        self.excerpt = self._get_excerpt()
        return super(Idea, self).save(*args, **kwargs)

    @classmethod
    def get_fields(cls):
        return cls._meta.fields
    
    class Meta:
        abstract = True

class Decision(Idea):

    TAGS_HELP_FIELD_TEXT = "Enter a list of tags separated by spaces."
    PROPOSAL_STATUS = 0
    CONSENSUS_STATUS = 1
    ARCHIVED_STATUS = 2

    STATUS_CHOICES = ( 
                  (PROPOSAL_STATUS, _('Proposal')),
                  (CONSENSUS_STATUS, _('Consensus')),
                  (ARCHIVED_STATUS, _('Archived')),
                  )

    #short_name = models.CharField(max_length=255, verbose_name=_('Name'))
    decided_date = models.DateField(null=True, blank=True,
        verbose_name=_('Decided date'))
    effective_date = models.DateField(null=True, blank=True,
        verbose_name=_('Effective date'))
    review_date = models.DateField(null=True, blank=True,
        verbose_name=_('Review date'))
    expiry_date = models.DateField(null=True, blank=True,
        verbose_name=_('Expiry date'))
    deadline = models.DateField(null=True, blank=True,
        verbose_name=_('Expiry date'))
    budget = models.CharField(blank=True, max_length=255,
        verbose_name=_('Budget/Resources'))
    people = models.CharField(blank=True, max_length=255,
        verbose_name=_('People'))
    author = models.ForeignKey(User, blank=True, null=True, editable=False, related_name='open_consent_author')
    watchers = models.ManyToManyField(User, blank=True, editable=False)
    status = models.IntegerField(choices=STATUS_CHOICES,
                                 default=PROPOSAL_STATUS,
                                 verbose_name=_('Status'))
    tags = TagField(null=True, blank=True, editable=True, 
                    help_text=TAGS_HELP_FIELD_TEXT)

    def is_watched(self, user):
        return user in self.watchers.all()
                        
    def add_watcher(self, user):
        if user not in self.watchers.all():
            self.watchers.add(user)
    
    def remove_watcher(self, user):
        if user in self.watchers.all():
            self.watchers.remove(user)
    
    def status_text(self):
        return self.STATUS_CHOICES[self.status][1]
    
    def unresolvedfeedback(self):
        answer = _("No")
        linked_feedback = self.feedback_set.all()
        for thisfeedback in linked_feedback:
            if (not thisfeedback.resolved):
                answer = _("Yes")
                break
            
        return answer

    def feedbackcount(self):
        return self.feedback_set.all().count()    
    
    unresolvedfeedback.short_description = _("Unresolved Feedback")
    
    @models.permalink
    def get_absolute_url(self):
        return ('edit_decision', (), {'decision_id':self.id})

    def save(self, author, *args, **kwargs):
        self.author = author

        #-----------------------------------#
        # This is email stuff. Would be good
        # if it could be hived off to a signal
        #-  --------------------------------#
        # ||
        # \/
        #record newness before saving
        if self.id:
            type='status_change'
            old = Decision.objects.get(id=self.id)
            if old.status != self.status:
                type='status_change'
            else:
                type='content_change'
        else:
            old = None
            type='new'
                    
        super(Decision, self).save(*args, **kwargs)

        email = OpenConsentEmailMessage(type=type,
                                        object = self,
                                        old_object = old)  

        email.send()
        
class Feedback(Idea):

    QUESTION_STATUS = 0
    DANGER_STATUS = 1
    SIGNIFICANT_CONCERNS_STATUS = 2
    CONSENT_STATUS = 3
    HAPPY_STATUS = 4
    DELIGHTED_STATUS = 5

    RATING_CHOICES = ( 
                  (QUESTION_STATUS, _('Question')),
                  (DANGER_STATUS, _('Danger')),
                  (SIGNIFICANT_CONCERNS_STATUS, _('Significant Concerns')),
                  (CONSENT_STATUS, _('Consent')),
                  (HAPPY_STATUS, _('Happy')),
                  (DELIGHTED_STATUS, _('Delighted')),
                  )
    
    #short_name = models.CharField(max_length=255, verbose_name=_('Feedback'))
    decision = models.ForeignKey('Decision', verbose_name=_('Decision'))
    resolved = models.BooleanField(verbose_name=_('Resolved'))
    rating = models.IntegerField(choices=RATING_CHOICES,
                                 verbose_name=_('Rating'),
                                 null=True, 
                                 blank=True )
