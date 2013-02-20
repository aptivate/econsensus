#error_css_class is very useful when you're rendering a form.as_p
#However the people at django don't want to put it on their own forms:
#https://code.djangoproject.com/ticket/17921

from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, PasswordChangeForm

class CustomAuthenticationForm(AuthenticationForm):
    error_css_class = 'error'
    required_css_class = 'required'

class CustomPasswordResetForm(PasswordResetForm):
    error_css_class = 'error'
    required_css_class = 'required'

class CustomPasswordChangeForm(PasswordChangeForm):
    error_css_class = 'error'
    required_css_class = 'required'
