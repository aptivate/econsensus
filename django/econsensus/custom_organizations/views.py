from organizations.views import OrganizationUserCreate, OrganizationUserUpdate, OrganizationUserDelete
from forms import CustomOrganizationUserForm, CustomOrganizationUserAddForm
from guardian.shortcuts import remove_perm

class CustomOrganizationUserUpdate(OrganizationUserUpdate):
    form_class = CustomOrganizationUserForm

    def get_initial(self):
        super(CustomOrganizationUserUpdate, self).get_initial()
        is_editor = self.object.user.has_perm('edit_decisions_feedback', self.object.organization)
        self.initial = {"is_editor":is_editor}
        return self.initial

class CustomOrganizationUserCreate(OrganizationUserCreate):
    form_class = CustomOrganizationUserAddForm

#Delete unused permissions!
class CustomOrganizationUserDelete(OrganizationUserDelete):
    def delete(self, *args, **kwargs):
        org_user = self.get_object()
        remove_perm('edit_decisions_feedback', org_user.user, org_user.organization)
        return super(CustomOrganizationUserDelete,self).delete(*args, **kwargs)
    