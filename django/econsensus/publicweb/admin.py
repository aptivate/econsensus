from django.contrib import admin
from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm

from guardian.admin import GuardedModelAdmin
from organizations.models import Organization

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
        (None, {'fields': ('description', 'organization',
                           ('effective_date','decided_date'),
                           ('review_date','expiry_date'),
                           'budget','people', 'status',)}),
    ]

    list_display = ('id', 'description', 'unresolvedfeedback', 'decided_date', 'effective_date', 'review_date', 'expiry_date', 'budget', 'people', 'organization')
    search_fields = ('description',)
    list_filter = ('status', 'decided_date', 'effective_date', 'review_date')
    inlines = (FeedbackInline,)
    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(attrs={'size':'86'})},
        }

    def save_model(self, request, obj, form, change):
        obj.editor = request.user
        obj.last_status = obj.status
        obj.save()

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('description','resolved')

class CustomUserCreationForm(UserCreationForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email already used")
        return email

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Decision, DecisionAdmin)
