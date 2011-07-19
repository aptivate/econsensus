# Create your forms here.

from django import forms
from models import Decision, Concern
import tinymce.widgets

from django.utils.translation import ugettext_lazy as _
from django.forms.models import inlineformset_factory
from django.forms.fields import ChoiceField

from publicweb.widgets import JQueryUIDateWidget

mce_attrs_setting = {
            "theme" : "advanced",
            "theme_advanced_buttons1" : "bold,italic,underline,link,unlink," +
                "bullist,blockquote,undo",
            "theme_advanced_buttons2" : "",
            "theme_advanced_buttons3" : "",
            }

class ConcernForm(forms.ModelForm):
    class Meta:
        model = Concern
        widgets = {'short_name': forms.TextInput(attrs={'size':'70'}),
                   'description': tinymce.widgets.TinyMCE(attrs={'cols': 80, 'rows': 20})}

ConcernFormSet = inlineformset_factory(Decision, Concern, 
                                       fields=('short_name','description','resolved',),
                                       form=ConcernForm)

class DecisionForm(forms.ModelForm):
    class Meta:
        model = Decision
        widgets = {'short_name': forms.TextInput(attrs={'size':'70'}),
                   'description': tinymce.widgets.TinyMCE(attrs={'cols': 80, 'rows': 20},
                                                          mce_attrs=mce_attrs_setting),
                   'concerns': tinymce.widgets.TinyMCE(mce_attrs=mce_attrs_setting),
                   'decided_date': JQueryUIDateWidget,
                   'effective_date': JQueryUIDateWidget,
                   'review_date': JQueryUIDateWidget,
                   'expiry_date': JQueryUIDateWidget,
                   'budget': forms.TextInput(attrs={'size':'70'}),
                   'people': forms.TextInput(attrs={'size':'70'})
                   }

EXTRA_CHOICE = (4, _('All'))

class FilterForm(forms.Form):
    #this seems clunky...
    list_choices = list(Decision.STATUS_CHOICES)
    list_choices.append(EXTRA_CHOICE)
    FILTER_CHOICES = tuple(list_choices)
    
    status = ChoiceField(choices=FILTER_CHOICES,
                         label = _('Status'),
                         initial=EXTRA_CHOICE[0],
                         required=False,
                         widget = forms.Select(attrs={'onchange':'this.form.submit()'}))
    
