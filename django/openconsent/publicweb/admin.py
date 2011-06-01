from django.contrib import admin
from django.db import models
from django import forms

from models import Decision, Group, Concern

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

    fieldsets = [
        (None, {'fields': ('short_name','description', 
                           ('effective_date','decided_date','review_date','expiry_date'),
                           'budget','people','group')}),
    ]

    list_display = ('short_name','decided_date','effective_date','review_date','expiry_date','budget','people','group')
    search_fields = ('short_name',)
    list_filter = ('decided_date','effective_date','review_date','expiry_date',)
    inlines = (ConcernInline,)
    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(attrs={'size':'86'})},
        }

class ConcernAdmin(admin.ModelAdmin):
    list_display = ('short_name','description','resolved')
        
admin.site.register(Group)
admin.site.register(Concern,ConcernAdmin)
admin.site.register(Decision,DecisionAdmin)