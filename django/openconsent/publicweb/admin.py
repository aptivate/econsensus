from django.contrib import admin
from django.db import models
from django import forms
from django.contrib.auth.models import User

from models import Decision, Feedback

class FeedbackInline(admin.TabularInline):
    model = Feedback
    extra = 1
    fieldsets = [
        (None, {'fields': ('description', 'resolved')}),
    ]
    template = 'admin/tabular.html'
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows':5, 'cols':80})},
        }

class DecisionAdmin(admin.ModelAdmin):
#    can't get nested fields to work...
#    fields = [('effective_date','decided_date','review_date')]

    change_list_template = 'admin/decision_change_list.html'
    fieldsets = [
        (None, {'fields': ('description', 
                           ('effective_date','decided_date'),
                           ('review_date','expiry_date'),
                           'budget','people', 'status',)}),
    ]

    list_display = ('description', 'unresolvedfeedback', 'decided_date', 'effective_date', 'review_date', 'expiry_date', 'budget', 'people')
    search_fields = ('description',)
    list_filter = ('decided_date', 'effective_date', 'review_date')
    inlines = (FeedbackInline,)
    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(attrs={'size':'86'})},
        }

    def save_model(self, request, obj, form, change):
        #obj.author = 
        obj.save(request.user)

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('description','resolved')

class UserForm(forms.ModelForm):
    class Meta:
        model = User

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email already used")
        return email

class UserAdmin(admin.ModelAdmin):
    form = UserForm

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
        
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Decision, DecisionAdmin)