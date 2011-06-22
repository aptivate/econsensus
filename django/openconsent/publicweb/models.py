from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
import tinymce.models
import tinymce.widgets
import datetime
    
class Decision(models.Model):
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
    
    def unresolvedconcerns(self):
        answer = "No"
        linked_concerns = self.concern_set.all()
        for thisconcern in linked_concerns:
            if (not thisconcern.resolved):
                answer = "Yes"
                break
            
        return answer
    
    unresolvedconcerns.short_description = "Unresolved Concerns"
                        
    def __unicode__(self):
        return self.short_name
    
    def get_absolute_url(self):
        return ('decision_edit', (), {'decision_id':self.id})
    get_absolute_url = models.permalink(get_absolute_url)
    
class Concern(models.Model):
    short_name = models.CharField(max_length=255, verbose_name='Concern')
    decision = models.ForeignKey('Decision')
    description = tinymce.models.HTMLField(blank=True, 
                                           verbose_name='Concern Description')
    resolved = models.BooleanField()
    
    def __unicode__(self):
        return self.short_name
    