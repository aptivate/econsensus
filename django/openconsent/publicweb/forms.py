# Create your forms here.

from django import forms
from models import Decision, Feedback

from django.utils.translation import ugettext_lazy as _
from django.forms.fields import ChoiceField

from widgets import JQueryUIDateWidget

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        exclude = ("decision",)

class DecisionForm(forms.ModelForm):
    
    watch = forms.BooleanField(required=False, initial=True)
       
    class Meta:
        model = Decision
        widgets = {
                   'decided_date': JQueryUIDateWidget,
                   'effective_date': JQueryUIDateWidget,
                   'review_date': JQueryUIDateWidget,
                   'expiry_date': JQueryUIDateWidget
                   }

EXTRA_CHOICE = (3, _('All')) #pylint: disable-msg=E1102

#TODO: Sort and filter forms have nothing to do with the app itself.
#Move to site when site and app are split.

class FilterForm(forms.Form):
    #this seems clunky...
    list_choices = list(Decision.STATUS_CHOICES)
    list_choices.append(EXTRA_CHOICE)
    FILTER_CHOICES = tuple(list_choices)
    filtar = ChoiceField(choices=FILTER_CHOICES,
                         label = _('Status'), #pylint: disable-msg=E1102
                         initial=EXTRA_CHOICE[0],
                         required=False,
                         widget = forms.Select(attrs={'onchange':'this.form.submit()'}))

class SortForm(forms.Form):
    
    #This is a more robust way of getting attributes to sort on.
    #However it generates a list that is probably too long.
    #TODO: Think about creating a mechanism to integrate the sorting with the fields that are / 
    #shown on the page
    #list_choices = [(field.name, field.name) for field in Decision.get_fields()]        
    
    list_choices = [('id', _('id')), #pylint: disable-msg=E1102
                    ('description', _('description')), #pylint: disable-msg=E1102
                    ('deadline', _('deadline'))] #pylint: disable-msg=E1102
    sort = ChoiceField(choices=list_choices,
                         label = _('Sort by'), #pylint: disable-msg=E1102
                         initial=list_choices[0],
                         required=False,
                         widget = forms.Select(attrs={'onchange':'this.form.submit()'}))
    
