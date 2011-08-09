from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.signals import pre_save
from django.conf import settings

import tinymce.models

# Ideally django-tinymce should be patched
# http://south.aeracode.org/wiki/MyFieldsDontWork
# http://code.google.com/p/django-tinymce/issues/detail?id=80
from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^tinymce\.models.\HTMLField"])

class Decision(models.Model):

    PROPOSAL_STATUS = 0
    CONSENSUS_STATUS = 1
    ARCHIVED_STATUS = 2

    STATUS_CHOICES = ( 
                  (PROPOSAL_STATUS, _('Proposal')),
                  (CONSENSUS_STATUS, _('Consensus')),
                  (ARCHIVED_STATUS, _('Archived')),
                  )

    short_name = models.CharField(max_length=255, verbose_name=_('Name'))
    decided_date = models.DateField(null=True, blank=True,
        verbose_name=_('Decided date'))
    effective_date = models.DateField(null=True, blank=True,
        verbose_name=_('Effective date'))
    review_date = models.DateField(null=True, blank=True,
        verbose_name=_('Review date'))
    expiry_date = models.DateField(null=True, blank=True,
        verbose_name=_('Expiry date'))
    budget = models.CharField(blank=True, max_length=255,
        verbose_name=_('Budget'))
    people = models.CharField(blank=True, max_length=255,
        verbose_name=_('People'))
    description = tinymce.models.HTMLField(blank=True,
        verbose_name=_('Description'))
    #author = models.ForeignKey(User, blank=True, editable=False, related_name='open_consent_author')
    subscribers = models.ManyToManyField(User, blank=True, editable=False)
    status = models.IntegerField(choices=STATUS_CHOICES,
                                 default=PROPOSAL_STATUS,
                                 verbose_name=_('Status'))

    def is_subscribed(self, user):
        return user in self.subscribers.all()
                        
    def add_subscriber(self, user):
        if user not in self.subscribers.all():
            self.subscribers.add(user)
 
    def remove_subscriber(self, user):
        if user in self.subscribers.all():
            self.subscribers.remove(user)
    
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
    
    unresolvedfeedback.short_description = _("Unresolved Feedback")
    
    def __unicode__(self):
        return self.short_name
    
    def get_absolute_url(self):
        return ('edit_decision', (), {'decision_id':self.id})
    get_absolute_url = models.permalink(get_absolute_url)

    def save(self, *args, **kwargs):

        #record newness before saving
        exists = self.id
                
        super(Decision, self).save(*args, **kwargs)
        
        if exists:
            title = "Open Consent: Item %s [%s] has changed" % (self.short_name, self.status_text())
            content = "URL to this decision: %s" % self.get_absolute_url()
            queryset = self.subscribers.all()
        
        else:
            title = "Open Consent: A new item has been created."
            content = "URL to this decision: %s" % self.get_absolute_url() 
            queryset = User.objects.all()

        mailing_list = []        
        for this_user in queryset:
            if this_user.email:
                mailing_list.append(this_user.email)
             
        send_mail(title, content, settings.ADMINS[0][1], mailing_list)        
                
class Feedback(models.Model):

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
    
    short_name = models.CharField(max_length=255, verbose_name=_('Feedback'))
    decision = models.ForeignKey('Decision', verbose_name=_('Decision'))
    description = tinymce.models.HTMLField(blank=True, 
                                           verbose_name=_('Feedback Description'))
    resolved = models.BooleanField(verbose_name=_('Resolved'))
    rating = models.IntegerField(choices=RATING_CHOICES,
                                 verbose_name=_('Rating'),
                                 null=True, 
                                 blank=True )
    def __unicode__(self):
        return self.short_name
    
#----------------------------------------------
# Signal Stuff.
#----------------------------------------------

#def sending_mail(sender, instance, **kwargs):
#
#    print "Doing stuff before save"
#    title = "Title"
#    content = "Content"
#    mailing_list = [] 
#    
#    if instance.id:
#        title = "Open Consent: Item %s [%s] has changed" % (instance.short_name, instance.status_text())
#        content = "URL to this decision: %s" % instance.get_absolute_url()
#        queryset = instance.subscribers.all()
#    else:
#        queryset = User.objects.all()
#        
#    for this_user in queryset:
#        if this_user.email:
#            mailing_list.append(this_user.email)
#         
#    send_mail(title, content, settings.ADMINS[0][1], mailing_list)        
#    
#pre_save.connect(sending_mail, sender=Decision)