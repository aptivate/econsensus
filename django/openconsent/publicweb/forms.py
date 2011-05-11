# Create your forms here.

import logging

from django import forms
from models import Decision
import tinymce.widgets

class DecisionForm(forms.ModelForm):
    class Meta:
        model = Decision
        widgets = {'description': tinymce.widgets.TinyMCE(mce_attrs={
            "theme" : "advanced",
            "theme_advanced_buttons1" : "bold,italic,underline,link,unlink," +
                "bullist,blockquote,undo",
            "theme_advanced_buttons2" : "",
            "theme_advanced_buttons3" : "",
            })}
