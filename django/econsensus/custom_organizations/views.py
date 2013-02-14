from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from organizations.models import Organization
from organizations.views import OrganizationCreate, OrganizationList, \
    OrganizationUserCreate, OrganizationUserUpdate, OrganizationUserDelete
from guardian.shortcuts import remove_perm
from forms import CustomOrganizationAddForm, CustomOrganizationUserForm, \
    CustomOrganizationUserAddForm

class CustomOrganizationCreate(OrganizationCreate):
    form_class = CustomOrganizationAddForm

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

class CustomOrganizationList(OrganizationList):
    '''
    If the user only belongs to one organization then
    take them to that organizations proposal page, otherwise
    take them to the organization list page.
    Note this is bound to the publicweb app.
    '''
    def get(self, request, *args, **kwargs):
        try:
            users_org = Organization.objects.get(users=request.user)
            return HttpResponseRedirect(reverse('publicweb_item_list', args = [users_org.slug, 'proposal']))
        except:
            return super(CustomOrganizationList,self).get(request, *args, **kwargs)
