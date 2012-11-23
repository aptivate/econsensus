from organizations.views import OrganizationUserCreate, OrganizationUserUpdate, OrganizationUserDelete
from forms import CustomOrganizationUserForm, CustomOrganizationUserAddForm

class CustomOrganizationUserUpdate(OrganizationUserUpdate):
    form_class = CustomOrganizationUserForm

    def get_initial(self):
        super(CustomOrganizationUserUpdate, self).get_initial()
        is_editor = self.object.user.has_perm('edit_decisions_feedback', self.object.organization)
        self.initial = {"is_editor":is_editor}
        return self.initial

class CustomOrganizationUserCreate(OrganizationUserCreate):
    form_class = CustomOrganizationUserAddForm

#Remember to delete unused permissions!
#class CustomOrganizationUserDelete(OrganizationUserDelete):
#    pass