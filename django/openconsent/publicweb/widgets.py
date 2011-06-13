import floppyforms as forms

class JQueryUIDateWidget(forms.DateInput):
    template_name = 'datepicker.html'
    input_type = 'text'
    class Media:
        js = ('https://ajax.googleapis.com/ajax/libs/jquery/1.6.1/jquery.min.js',
              'https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.13/jquery-ui.min.js',
        )

        css = {
            'all': (
                '/media/jquery/jquery-ui.css',
            )
        }

    def __init__(self, attrs={}, format=None):
        super(JQueryUIDateWidget, self).__init__(attrs={'class': 'vDateField', 'size': '10'}, format=format)
