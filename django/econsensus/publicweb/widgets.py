from django import forms
from django.conf import settings

class JQueryUIDateWidget(forms.DateInput):
    class Media:
        js = ('https://ajax.googleapis.com/ajax/libs/jquery/1.6.1/jquery.min.js',
              'https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.13/jquery-ui.min.js',
              settings.STATIC_URL + 'js/calendar.js',
              settings.STATIC_URL + 'js/edit.js',
        )
        
        css = {
            'all': (
                settings.STATIC_URL + 'jquery/jquery-ui.css',
            )
        }

    def __init__(self, *args, **kwargs):
            super(JQueryUIDateWidget, self).__init__(attrs={'class': 'vDateField', 'size': '10'}, format=format)
