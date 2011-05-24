# Create your forms here.

import logging

from django import forms
from models import Decision, Group, Concern
import tinymce.widgets

from django.forms.models import inlineformset_factory

mce_attrs_setting = {
            "theme" : "advanced",
            "theme_advanced_buttons1" : "bold,italic,underline,link,unlink," +
                "bullist,blockquote,undo",
            "theme_advanced_buttons2" : "",
            "theme_advanced_buttons3" : "",
            }
        
ConcernFormSet = inlineformset_factory(Decision, Concern, fields=('short_name',))

class DecisionForm(forms.ModelForm):
    class Meta:
        model = Decision
        widgets = {'description': tinymce.widgets.TinyMCE(mce_attrs=mce_attrs_setting),
                   'concerns': tinymce.widgets.TinyMCE(mce_attrs=mce_attrs_setting)}

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
