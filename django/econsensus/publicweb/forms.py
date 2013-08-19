# Create your forms here.

from django import forms
from models import Decision, Feedback
from django.contrib.auth.models import User


from django.utils.translation import ugettext_lazy as _
from django.forms.fields import ChoiceField

from widgets import JQueryUIDateWidget
from parsley.decorators import parsleyfy
from actionitems.models import ActionItem
from actionitems.forms import ActionItemCreateForm, ActionItemUpdateForm

class YourDetailsForm(forms.ModelForm):

    class Meta:
        model = User
        exclude = ('is_staff', 'is_superuser', 'is_active', 'last_login',
                'date_joined', 'groups', 'user_permissions', 'password')

    def clean_email(self):
        if self.instance.email == self.cleaned_data['email']:
            return self.cleaned_data['email']
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))
        return self.cleaned_data['email']


class FeedbackForm(forms.ModelForm):
    minor_edit = forms.BooleanField(required=False, initial=False)
    class Meta:
        model = Feedback
        exclude = ("decision",)

@parsleyfy
class DecisionForm(forms.ModelForm):
    
    watch = forms.BooleanField(required=False, initial=True)
    minor_edit = forms.BooleanField(required=False, initial=False)
    class Meta:
        model = Decision
        exclude = ('organization',)
        widgets = {
                   'decided_date': JQueryUIDateWidget,
                   'effective_date': JQueryUIDateWidget,
                   'review_date': JQueryUIDateWidget,
                   'expiry_date': JQueryUIDateWidget,
                   'archived_date': JQueryUIDateWidget,
                   'deadline': JQueryUIDateWidget
                   }

EXTRA_CHOICE = (3, _('All')) #pylint: disable=E1102

@parsleyfy
class EconsensusActionItemCreateForm(ActionItemCreateForm):
    pass
#TODO: Sort and filter forms have nothing to do with the app itself.
#Move to site when site and app are split.

@parsleyfy
class EconsensusActionItemUpdateForm(ActionItemUpdateForm):
    pass

class FilterForm(forms.Form):
    #this seems clunky...
    list_choices = list(Decision.STATUS_CHOICES)
    list_choices.append(EXTRA_CHOICE)
    FILTER_CHOICES = tuple(list_choices)
    filtar = ChoiceField(choices=FILTER_CHOICES,
                         label = _('Status'), #pylint: disable=E1102
                         initial=EXTRA_CHOICE[0],
                         required=False,
                         widget = forms.Select(attrs={'onchange':'this.form.submit()'}))
