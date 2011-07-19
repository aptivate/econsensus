from django.contrib import admin
from django.db import models
from django import forms

from models import Decision, Feedback

class FeedbackInline(admin.TabularInline):
    model = Feedback
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

    list_display = ('short_name','unresolvedfeedback', 'decided_date','effective_date','review_date','expiry_date','budget','people')
    search_fields = ('short_name',)
    list_filter = ('decided_date','effective_date','review_date',)
    inlines = (FeedbackInline,)
    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(attrs={'size':'86'})},
        }

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('short_name','description','resolved')
        
admin.site.register(Feedback,FeedbackAdmin)
admin.site.register(Decision,DecisionAdmin)