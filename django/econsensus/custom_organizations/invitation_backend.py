from organizations.backends.tokens import RegistrationTokenGenerator
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.http import Http404
from django.utils.translation import ugettext as _


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
    form_class = CustomUserRegistrationForm

    def activate_view(self, request, user_id, token):
        """
        Activates the given User by setting `is_active` to true if the provided
        information is verified.
        """
        try:
            user = self.user_model.objects.get(id=user_id, is_active=False)
        except self.user_model.DoesNotExist:
            raise Http404(_("Your URL may have expired."))
        if not RegistrationTokenGenerator().check_token(user, token):
            raise Http404(_("Your URL may have expired."))
        form = self.get_form(data=request.POST or None, instance=user)
        if form.is_valid():
            form.instance.is_active = True
            user = form.save()
            user.set_password(form.cleaned_data['password'])
            user.save()
            for org in user.organization_set.filter(is_active=False):
                org.is_active = True
                org.save()
            user = authenticate(username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'])
            login(request, user)
            return redirect(self.get_success_url())
        return render(request, 'registration/registration_form.html',
                {'form': form})

