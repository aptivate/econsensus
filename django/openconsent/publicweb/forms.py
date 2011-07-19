# Create your forms here.

from django import forms
from models import Decision, Concern
import tinymce.widgets

from django.forms.models import inlineformset_factory
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
        widgets = {'short_name': forms.TextInput(attrs={'size':''}),
                   'description': tinymce.widgets.TinyMCE(attrs={'cols': 80, 'rows': 5})}

ConcernFormSet = inlineformset_factory(Decision, Concern, 
                                       fields=('short_name','description','resolved',),
                                       form=ConcernForm)

class DecisionForm(forms.ModelForm):
    class Meta:
        model = Decision
        widgets = {'short_name': forms.TextInput(attrs={'size':''}),
                   'description': tinymce.widgets.TinyMCE(attrs={'cols': 80, 'rows': 5},
                                                          mce_attrs=mce_attrs_setting),
                   'concerns': tinymce.widgets.TinyMCE(mce_attrs=mce_attrs_setting),
                   'decided_date': JQueryUIDateWidget,
                   'effective_date': JQueryUIDateWidget,
                   'review_date': JQueryUIDateWidget,
                   'expiry_date': JQueryUIDateWidget,
                   'budget': forms.TextInput(attrs={'size':''}),
                   'people': forms.TextInput(attrs={'size':''})
                   }
        
