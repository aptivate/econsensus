# Create your forms here.

from django import forms
from models import Decision, Feedback
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

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        widgets = {'short_name': forms.TextInput(),
                   'description': tinymce.widgets.TinyMCE(attrs={'rows': 20})
                   }

FeedbackFormSet = inlineformset_factory(Decision, Feedback, 
                                       fields=('short_name','description','resolved','rating'),
                                       form=FeedbackForm)

class DecisionForm(forms.ModelForm):
    class Meta:
        model = Decision
        widgets = {'short_name': forms.TextInput(),
                   'description': tinymce.widgets.TinyMCE(attrs={'rows': 5},
                                                          mce_attrs=mce_attrs_setting),
                   'feedback': tinymce.widgets.TinyMCE(mce_attrs=mce_attrs_setting),
                   'decided_date': JQueryUIDateWidget,
                   'effective_date': JQueryUIDateWidget,
                   'review_date': JQueryUIDateWidget,
                   'expiry_date': JQueryUIDateWidget,
                   'budget': forms.TextInput(),
                   'people': forms.TextInput()
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
    
