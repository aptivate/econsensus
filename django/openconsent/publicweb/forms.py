# Create your forms here.

import logging

from django import forms
from models import Decision

class DecisionForm(forms.ModelForm):
    class Meta:
        model = Decision
