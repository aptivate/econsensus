from registration.backends.default import DefaultBackend
from forms import RecaptchaRegistrationForm

class RecaptchaRegistrationBackend(DefaultBackend):
    def get_form_class(self, request):
        print "***Doing recaptcha shit***"
        return RecaptchaRegistrationForm