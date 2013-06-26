from django import forms

from organizations.models import Organization, get_user_model
from organizations.utils import create_organization
from organizations.forms import OrganizationUserForm, OrganizationUserAddForm
from guardian.shortcuts import assign, remove_perm
from registration.forms import RegistrationFormUniqueEmail
from django.utils.translation import ugettext_lazy as _


# Create another Registration form so we can add extra fields 
# to the sign up process (first_name and last_name)
# These fields are caught by the new_user signal
# and saved into the User model
class CustomUserSignupRegistrationForm(RegistrationFormUniqueEmail):
    """Form class for completing a user's registration and activating the
    User."""
    first_name = forms.CharField(max_length=30, label = _("First name"))
    last_name = forms.CharField(max_length=30, label = _("Last name"))

    def __init__(self, *args, **kwargs):
        super(CustomUserSignupRegistrationForm, self).__init__(*args, **kwargs)
        self.initial['username'] = ''
        self.fields.keyOrder = ['username', 'first_name', 'last_name',
                                'email', 'password1', 'password2']



# Override the UserRegistrationForm so we can pick and choose
# which fields to use and change the labels
class CustomUserRegistrationForm(forms.ModelForm):
    """Form class for completing a user's registration and activating the
    User."""
    email = forms.CharField(label = _("E-mail"))
    password = forms.CharField(max_length=30, widget=forms.PasswordInput, 
                label = _("Password"))
    password_confirm = forms.CharField(max_length=30,
            widget=forms.PasswordInput, label = _("Password (again)"))

    def __init__(self, *args, **kwargs):
        super(CustomUserRegistrationForm, self).__init__(*args, **kwargs)
        self.initial['username'] = ''

    class Meta:
        model = get_user_model()
        exclude = ('is_staff', 'is_superuser', 'is_active', 'last_login',
                'date_joined', 'groups', 'user_permissions')


# Completely override OrganizationForm and OrganizationAddForm from 
# organizations.forms because we don't want to allow ownership changes via UI, 
# and we want the owner of new Organizations to be the creating user.
class CustomOrganizationForm(forms.ModelForm):
    """
    For editing Organizations.
    """

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(CustomOrganizationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Organization
        exclude = ('slug', 'users', 'is_active')

class CustomOrganizationAddForm(CustomOrganizationForm):
    """
    For creating new Organizations.
    Set the owner to be the request user. The slug, will be auto-generated 
    from the name.
    """

    def save(self, **kwargs):
        is_active = True
        user = self.request.user
        organization = create_organization(user,
                                           self.cleaned_data['name'],
                                           '',  # Empty slug to be autofilled
                                           is_active=is_active)
        assign('edit_decisions_feedback',
               organization.owner.organization_user.user,
               organization)
        return organization

class CustomOrganizationUserForm(OrganizationUserForm):
    is_editor = forms.BooleanField(required=False)

    def save(self, commit=True):
        if self.cleaned_data['is_editor']:
            assign('edit_decisions_feedback', self.instance.user, self.instance.organization)
        else:
            remove_perm('edit_decisions_feedback', self.instance.user, self.instance.organization)
        return super(CustomOrganizationUserForm, self).save(commit=commit)

class CustomOrganizationUserAddForm(OrganizationUserAddForm):
    is_editor = forms.BooleanField(required=False, initial=True)

    def save(self, commit=True):
        self.instance = super(CustomOrganizationUserAddForm, self).save(commit=commit)
        if self.cleaned_data['is_editor']:
            assign('edit_decisions_feedback', self.instance.user, self.instance.organization)
        else:
            remove_perm('edit_decisions_feedback', self.instance.user, self.instance.organization)
        return self.instance
