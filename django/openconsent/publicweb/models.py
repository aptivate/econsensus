from django.db import models
from django.core.urlresolvers import reverse

import tinymce.models
#import tinymce.widgets
import datetime
    
class Decision(models.Model):
    short_name = models.CharField(max_length=255, verbose_name='Name')
    decided_date = models.DateField(null=True, blank=True,
        verbose_name='Decided date')
    effective_date = models.DateField(null=True, blank=True,
        verbose_name='Effective date')
    review_date = models.DateField(null=True, blank=True,
        verbose_name='Review date')
    expiry_date = models.DateField(null=True, blank=True,
        verbose_name='Expiry date')
    budget = models.CharField(blank=True, max_length=255,
        verbose_name='Budget')
    people = models.CharField(blank=True, max_length=255,
        verbose_name='People')
    description = tinymce.models.HTMLField(blank=True,
        verbose_name='Description')
    
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
        x = reverse('decision_edit', args=[self.id])
        return x
    
class Concern(models.Model):
    short_name = models.CharField(max_length=255, verbose_name='Concern')
    decision = models.ForeignKey('Decision')
    description = models.TextField(blank=True, verbose_name='Concern Description')
    resolved = models.BooleanField()
    
    def __unicode__(self):
        return self.short_name
    