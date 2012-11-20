from django import forms
from organizations.forms import OrganizationUserForm, OrganizationUserAddForm
from guardian.shortcuts import assign, remove_perm

class CustomOrganizationUserForm(OrganizationUserForm):
    #lookup the permission
    #self.instance.user.has_perm('edit_decisions_feedback', self.instance.organization)
    is_editor = forms.BooleanField(required=False)     

    def save(self, commit=True):
        if self.cleaned_data['is_editor']:
            assign('edit_decisions_feedback', self.instance.user, self.instance.organization)
        else:
            remove_perm('edit_decisions_feedback', self.instance.user, self.instance.organization)
        return super(CustomOrganizationUserForm, self).save(commit=commit)
