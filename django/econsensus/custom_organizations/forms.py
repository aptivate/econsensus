from django import forms

from organizations.models import Organization
from organizations.utils import create_organization
from organizations.forms import OrganizationUserForm, OrganizationUserAddForm
from guardian.shortcuts import assign, remove_perm


class CustomOrganizationAddForm(forms.ModelForm):

    """
    Completely override organizations.forms.OrganizationAddForm
    The slug, will be auto-generated from the name, and the user is the
    request user.
    """

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(CustomOrganizationAddForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Organization
        exclude = ('slug', 'users', 'is_active')

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
