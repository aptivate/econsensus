from django.db import models
from django.utils.translation import ugettext_lazy as _
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
    status = models.IntegerField(choices=STATUS_CHOICES,
                                 default=PROPOSAL_STATUS,
                                 verbose_name=_('Status'))
    
    def status_text(self):
        return self.STATUS_CHOICES[self.status][1]
    
    def unresolvedconcerns(self):
        answer = _("No")
        linked_concerns = self.concern_set.all()
        for thisconcern in linked_concerns:
            if (not thisconcern.resolved):
                answer = _("Yes")
                break
            
        return answer
    
    unresolvedconcerns.short_description = _("Unresolved Concerns")
                        
    def __unicode__(self):
        return self.short_name
    
    def get_absolute_url(self):
        return ('decision_edit', (), {'decision_id':self.id})
    get_absolute_url = models.permalink(get_absolute_url)
    
class Concern(models.Model):
    short_name = models.CharField(max_length=255, verbose_name=_('Concern'))
    decision = models.ForeignKey('Decision', verbose_name=_('Decision'))
    description = tinymce.models.HTMLField(blank=True, 
                                           verbose_name=_('Concern Description'))
    resolved = models.BooleanField(verbose_name=_('Resolved'))
    
    def __unicode__(self):
        return self.short_name
    