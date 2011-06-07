from django.contrib import admin
from django.db import models
from django import forms
from django.shortcuts import get_object_or_404
from django.forms import MediaDefiningClass

from functools import partial

from models import Decision, Group, Concern
from views import DecisionTable


class GroupAdmin(admin.ModelAdmin):
    model = Group
    
    change_form_template = 'admin/group_change_form.html'
    
    def change_view(self, request, object_id, extra_context=None):
                
        group = get_object_or_404(Group, pk=object_id)
        
        decisions = group.decision_set.all()
        
        extra_context = {
            'decisions': decisions,
        }
        return super(GroupAdmin, self).change_view(request, object_id,
            extra_context=extra_context)
    

class ConcernInline(admin.TabularInline):
    model = Concern
    extra = 1
    fieldsets = [
        (None, {'fields': ('short_name','description', 'resolved')}),
    ]
    template = 'admin/tabular.html'
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows':5, 'cols':80})},
        }

class DecisionAdmin(admin.ModelAdmin):
#    can't get nested fields to work...
#    fields = ['short_name',('effective_date','decided_date','review_date')]

    change_list_template = 'admin/decision_change_list.html'
        
    fieldsets = [
        (None, {'fields': ('short_name','description', 
                           ('effective_date','decided_date'),
                           ('review_date','expiry_date'),
                           'budget','people')}),
    ]

    list_display = ('short_name','decided_date','effective_date','review_date','expiry_date','budget','people')
    search_fields = ('short_name',)
    list_filter = ('decided_date','effective_date','review_date',)
    inlines = (ConcernInline,)
    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(attrs={'size':'86'})},
        }

class ConcernAdmin(admin.ModelAdmin):
    list_display = ('short_name','description','resolved')
        
admin.site.register(Concern,ConcernAdmin)
admin.site.register(Decision,DecisionAdmin)