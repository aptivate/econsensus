from django.core.urlresolvers import reverse

from organizations.backends.defaults import InvitationBackend

from custom_organizations.forms import CustomUserRegistrationForm

class CustomInvitationBackend(InvitationBackend):
    """
    Customise django-organizations' default InvitationBackend so that we can 
    use our own form so we can fine tune the fields we want and make it look 
    the same as registration sign up
    """
    form_class = CustomUserRegistrationForm

    def get_success_url(self):
        return reverse('publicweb_root')

