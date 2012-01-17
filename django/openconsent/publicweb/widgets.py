import floppyforms as forms
from django.conf import settings

class JQueryUIDateWidget(forms.DateInput):
    template_name = 'datepicker.html'
    input_type = 'text'
    class Media:
        js = ('https://ajax.googleapis.com/ajax/libs/jquery/1.6.1/jquery.min.js',
              'https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.13/jquery-ui.min.js',
              settings.MEDIA_URL + 'js/edit.js',
        )

        css = {
            'all': (
                settings.MEDIA_URL + '/jquery/jquery-ui.css',
            )
        }

    def __init__(self, *args, **kwargs):
        super(JQueryUIDateWidget, self).__init__(attrs={'class': 'vDateField', 'size': '10'}, format=format)
