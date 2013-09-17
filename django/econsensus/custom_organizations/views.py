from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.edit import CreateView

from guardian.shortcuts import remove_perm

from organizations.backends import invitation_backend
from organizations.views import OrganizationCreate,\
                                OrganizationUpdate,\
                                OrganizationDetail,\
                                OrganizationUserCreate,\
                                OrganizationUserUpdate,\
                                OrganizationUserDelete,\
                                OrganizationUserRemind,\
                                OrganizationUserList, \
                                BaseOrganizationUserDelete, \
                                BaseOrganizationDetail
from organizations.mixins import AdminRequiredMixin, \
                                 OrganizationMixin

from custom_organizations.forms import CustomOrganizationForm,\
                                    CustomOrganizationAddForm,\
                                    CustomOrganizationUserForm,\
                                    CustomOrganizationUserAddForm, \
                                    GroupAddForm
from django.http import Http404
from organizations.models import Organization
from publicweb.models import Feedback
from custom_organizations.models import Group

class OrganizationAdminView(BaseOrganizationDetail):
    model = Organization
    template_name = 'organizations/organization_admin.html'

class GroupCreate(OrganizationMixin, CreateView):
    # model = Group
    form_class = GroupAddForm
    template_name = 'organizations/organizationgroup_form.html'

    def get_success_url(self):
        return reverse("organization_list")

    def get_form_kwargs(self):
        kwargs = super(GroupCreate, self).get_form_kwargs()
        kwargs.update({'organization': self.get_organization(),
            'request': self.request})
        return kwargs

    # def get(self, request, *args, **kwargs):
    #     self.organization = self.get_organization()
    #     context = self.get_context_data(organization=self.organization)
    #     return self.render_to_response(context)

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
class CustomOrganizationUserDelete(BaseOrganizationUserDelete):
    def _is_admin(self, request, organization_pk):
        organization = get_object_or_404(Organization, pk=organization_pk)
        return organization.is_admin(request.user) or request.user.is_superuser
                    
    def _is_current_user(self, request, user_pk):
        """
        Checks the user being accessed is the one currently logged in
        """
        return request.user.id == int(user_pk)
            
    def dispatch(self, request, *args, **kwargs):
        organization_pk = kwargs.get('organization_pk', None)
        user_pk = kwargs.get('user_pk', None)
        if not self._is_admin(request, organization_pk) and not \
            self._is_current_user(request, user_pk):
            raise Http404
        return super(CustomOrganizationUserDelete, self).dispatch(
             request, *args, **kwargs) 
    
    def delete(self, *args, **kwargs):
        org_user = self.get_object()
        remove_perm('edit_decisions_feedback', org_user.user, org_user.organization)
        decisions = org_user.organization.decision_set.all()
        for decision in decisions:
            decision.watchers.filter(user=org_user.user).delete()
        for feedback in Feedback.objects.filter(decision__in=decisions):
            feedback.watchers.filter(user=org_user.user).delete()
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
