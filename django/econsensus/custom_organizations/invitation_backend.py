from organizations.backends.defaults import InvitationBackend

from custom_organizations.forms import CustomUserRegistrationForm

class CustomInvitationBackend(InvitationBackend):
    """
    Customise django-organizations' default InvitationBackend so that we can
    provide our own body and subject templates for the emails.
    """
    invitation_subject = 'email/invitation_subject.txt'
    invitation_body = 'email/invitation_body.html'
    reminder_body = 'email/reminder_body.html'
    # Use our own form so we can fine tune the fields we want
    # and make it look the same as registration sign up
    form_class = CustomUserRegistrationForm


