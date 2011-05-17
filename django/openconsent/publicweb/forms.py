# Create your forms here.

import logging

from django import forms
from models import Decision
from models import Group
import tinymce.widgets

class DecisionForm(forms.ModelForm):
    class Meta:
        model = Decision

        mce_attrs_setting = {
            "theme" : "advanced",
            "theme_advanced_buttons1" : "bold,italic,underline,link,unlink," +
                "bullist,blockquote,undo",
            "theme_advanced_buttons2" : "",
            "theme_advanced_buttons3" : "",
            }
        
        widgets = {'description': tinymce.widgets.TinyMCE(mce_attrs=mce_attrs_setting),
                   'concerns': tinymce.widgets.TinyMCE(mce_attrs=mce_attrs_setting)}

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
