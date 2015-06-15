from django import forms

from organizations.models import Organization, get_user_model, OrganizationOwner, OrganizationUser
from organizations.utils import create_organization
from organizations.backends.forms import UserRegistrationForm
from organizations.forms import OrganizationUserForm, OrganizationUserAddForm
from guardian.shortcuts import assign_perm, remove_perm
from registration.forms import RegistrationFormUniqueEmail
from registration.signals import user_registered
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _


# Subclass the default Registration form so we can add extra fields 
# to the sign up process (first_name and last_name)
# These fields are caught by the user_registered signal
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

@receiver(user_registered)
def user_created(sender, user, request, **kwargs):
    form = CustomUserSignupRegistrationForm(request.POST)
    user.first_name = form.data['first_name']
    user.last_name = form.data['last_name']
    user.save()


# Subclass the UserRegistrationForm so we can change the labels
class CustomUserRegistrationForm(UserRegistrationForm):
    """Form class for completing a user's registration and activating the
    User."""
    email = forms.CharField(label = _("E-mail"))
    password = forms.CharField(max_length=30, widget=forms.PasswordInput, 
                label = _("Password"))
    password_confirm = forms.CharField(max_length=30,
            widget=forms.PasswordInput, label = _("Password (again)"))

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
        assign_perm('edit_decisions_feedback',
               organization.owner.organization_user.user,
               organization)
        return organization

class CustomOrganizationUserForm(OrganizationUserForm):
    USER_TYPES = (
        ('admin', _("Admin (can edit and invite users)")),
        ('editor', _("Normal User")),
        ('viewer', _("Viewer Only (can't add or edit information)")),
    )
    user_type = forms.ChoiceField(required=True, choices=USER_TYPES) 

    def save(self, commit=True):
        self.instance.is_admin = (self.cleaned_data['user_type'] == 'admin')
        if self.cleaned_data['user_type'] != 'viewer':
            assign_perm('edit_decisions_feedback', self.instance.user, self.instance.organization)
        else:
            remove_perm('edit_decisions_feedback', self.instance.user, self.instance.organization)
        return super(CustomOrganizationUserForm, self).save(commit=commit)

class CustomOrganizationUserAddForm(OrganizationUserAddForm):
    USER_TYPES = (
        ('admin', _("Admin (can edit and invite users)")),
        ('editor', _("Normal User")),
        ('viewer', _("Viewer Only (can't add or edit information)")),
    )
    user_type = forms.ChoiceField(required=True, choices=USER_TYPES)

    def save(self, commit=True):
        self.cleaned_data['is_admin'] = (self.cleaned_data['user_type'] == 'admin')
        self.instance = super(CustomOrganizationUserAddForm, self).save(commit=commit)
        if self.cleaned_data['user_type'] != 'viewer':
            assign_perm('edit_decisions_feedback', self.instance.user, self.instance.organization)
        else:
            remove_perm('edit_decisions_feedback', self.instance.user, self.instance.organization)
        return self.instance


class ChangeOwnerForm(forms.ModelForm):
    class Meta:
        model = OrganizationOwner
        fields = ['organization_user']

    def __init__(self, *args, **kwargs):
        current_org_pk = kwargs.pop("current_org_pk")
        super(ChangeOwnerForm, self).__init__(*args, **kwargs)
        self.fields['organization_user'].queryset = OrganizationUser.objects.filter(organization=current_org_pk)
