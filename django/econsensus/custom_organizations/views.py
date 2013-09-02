from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from guardian.shortcuts import remove_perm

from organizations.backends import invitation_backend
from organizations.views import OrganizationCreate,\
                                OrganizationUpdate,\
                                OrganizationDetail,\
                                OrganizationUserCreate,\
                                OrganizationUserUpdate,\
                                OrganizationUserDelete,\
                                OrganizationUserRemind,\
                                OrganizationUserList
from organizations.mixins import AdminRequiredMixin

from custom_organizations.forms import CustomOrganizationForm,\
                                    CustomOrganizationAddForm,\
                                    CustomOrganizationUserForm,\
                                    CustomOrganizationUserAddForm
from django.http import Http404


class CustomOrganizationCreate(OrganizationCreate):
    form_class = CustomOrganizationAddForm

class CustomOrganizationUpdate(OrganizationUpdate):
    form_class = CustomOrganizationForm

    def get_success_url(self):
        return reverse("organization_list")


class CustomOrganizationUserList(AdminRequiredMixin, OrganizationUserList):
    def get(self, request, *args, **kwargs):
        self.organization = self.get_organization()
        self.object_list = self.organization.organization_users.all()
        self.inactive_list = self.organization.organization_users.filter(user__is_active=False)
        context = self.get_context_data(object_list=self.object_list,
                organization_users=self.object_list,
                inactive_users=self.inactive_list,
                organization=self.organization)
        return self.render_to_response(context)

class CustomOrganizationUserRemind(OrganizationUserRemind):

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        invitation_backend().send_reminder(self.object.user,
                **{'domain': get_current_site(self.request),
                    'organization': self.organization, 'sender': request.user})
        return redirect(reverse("organization_user_list", args=[str(self.organization.id)]))

class CustomOrganizationUserUpdate(OrganizationUserUpdate):
    form_class = CustomOrganizationUserForm

    def get_initial(self):
        super(CustomOrganizationUserUpdate, self).get_initial()
        is_editor = self.object.user.has_perm('edit_decisions_feedback', self.object.organization)
        self.initial = {"is_editor": is_editor}
        return self.initial

class CustomOrganizationUserCreate(OrganizationUserCreate):
    form_class = CustomOrganizationUserAddForm

# Delete unused permissions!
# And remove them as watchers on decisions for that organisation.
class CustomOrganizationUserDelete(OrganizationUserDelete):
    def delete(self, *args, **kwargs):
        org_user = self.get_object()
        remove_perm('edit_decisions_feedback', org_user.user, org_user.organization)
        for decision in org_user.organization.decision_set.all():
            decision.watchers.filter(user=org_user.user).delete()
        return super(CustomOrganizationUserDelete,self).delete(*args, **kwargs)
    
class CustomOrganizationDetail(AdminRequiredMixin, OrganizationDetail):
    pass

class CustomOrganizationUserLeave(CustomOrganizationUserDelete):
    """
       This view is necessary because CustomOrganizationUserDelete redirects to
       the CustomOrganizationUserList view, which regular users shouldn't be 
       able to access. When they leave an organisation, we send them back to 
       their organisations list.       
    """
    def get_success_url(self):
        return reverse('organization_list')
