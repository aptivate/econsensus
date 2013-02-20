from django import forms
from organizations.forms import OrganizationAddForm, OrganizationUserForm, OrganizationUserAddForm
from guardian.shortcuts import assign, remove_perm

class CustomOrganizationAddForm(OrganizationAddForm):
    
    def save(self, **kwargs):
        organization = super(CustomOrganizationAddForm, self).save(**kwargs)
        assign('edit_decisions_feedback', organization.owner.organization_user.user, organization)
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
