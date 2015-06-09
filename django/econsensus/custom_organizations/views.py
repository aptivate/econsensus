from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import UpdateView

from guardian.shortcuts import remove_perm

from organizations.backends import invitation_backend
from organizations.views import (OrganizationCreate,
                                 OrganizationUpdate,
                                 OrganizationDetail,
                                 OrganizationUserCreate,
                                 OrganizationUserUpdate,
                                 OrganizationUserRemind,
                                 OrganizationUserList,
                                 BaseOrganizationUserDelete,
                                 BaseOrganizationDetail)
from organizations.mixins import AdminRequiredMixin

from custom_organizations.forms import (CustomOrganizationForm,
                                        CustomOrganizationAddForm,
                                        CustomOrganizationUserForm,
                                        CustomOrganizationUserAddForm,
                                        ChangeOwnerForm)
from organizations.models import Organization, OrganizationOwner

from publicweb.models import Feedback


class OrganizationAdminView(BaseOrganizationDetail):
    model = Organization
    template_name = 'organizations/organization_admin.html'


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
        context = self.get_context_data(
            object_list=self.object_list,
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

    def compose_user_type(self, is_editor, is_admin):
        if is_admin: return 'admin'
        if is_editor: return 'editor'
        return 'viewer'

    def decompose_user_type(self, user_type):
        is_admin = user_type == 'admin'
        is_editor = user_type != 'observer'
        return is_admin, is_editor

    def get_initial(self):
        super(CustomOrganizationUserUpdate, self).get_initial()
        is_editor = self.object.user.has_perm('edit_decisions_feedback', self.object.organization)
        self.initial = {"user_type" : self.compose_user_type(is_editor, self.object.is_admin)}
        return self.initial


class CustomOrganizationUserCreate(OrganizationUserCreate):
    form_class = CustomOrganizationUserAddForm


# Delete unused permissions!
# And remove them as watchers on decisions for that organisation.
class CustomOrganizationUserDelete(BaseOrganizationUserDelete):

    def _check_access_perms(self, user):
        """ Leave covers the "removing self" case, so restrict to only admins
        """
        self.organization = self.get_organization()
        if not self.organization.is_admin(user) and not user.is_superuser:
            return HttpResponseForbidden(_("Sorry, admins only"))

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        response = self._check_access_perms(request.user)
        if response is not None:
            return response
        return super(CustomOrganizationUserDelete, self).dispatch(
            request, *args, **kwargs)

    def delete(self, *args, **kwargs):
        org_user = self.get_object()
        remove_perm('edit_decisions_feedback', org_user.user, org_user.organization)
        decisions = org_user.organization.decision_set.all()
        for decision in decisions:
            decision.watchers.filter(user=org_user.user).delete()
        # TODO: remove circular dependency back to Feedback - add method
        # on decision model to delete all watchers, and have that cascade
        # and then have that listen for the organization_user delete
        for feedback in Feedback.objects.filter(decision__in=decisions):
            feedback.watchers.filter(user=org_user.user).delete()
        return super(CustomOrganizationUserDelete, self).delete(*args, **kwargs)


class CustomOrganizationDetail(AdminRequiredMixin, OrganizationDetail):
    pass


class CustomOrganizationUserLeave(CustomOrganizationUserDelete):
    """
       This view is necessary because CustomOrganizationUserDelete redirects to
       the CustomOrganizationUserList view, which regular users shouldn't be
       able to access. When they leave an organisation, we send them back to
       their organisations list.
    """
    template_name = 'organizations/organizationuser_confirm_leave.html'

    def _check_access_perms(self, request, **kwargs):
        """ we set the user_pk to self in dispatch, and the organization/user
        combo is checked in get_object() (if that fails it does 404) - so don't
        worry about this. """
        pass

    def dispatch(self, request, *args, **kwargs):
        kwargs['user_pk'] = request.user.id
        return super(CustomOrganizationUserLeave, self).dispatch(
            request, *args, **kwargs)

    def get_success_url(self):
        return reverse('organization_list')


class ChangeOwnerView(UpdateView):
    model = OrganizationOwner
    form_class = ChangeOwnerForm
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse('organization_admin',
                kwargs={'organization_pk': self.object.organization.pk})

    def get_form_kwargs(self):
        kwargs = super(ChangeOwnerView, self).get_form_kwargs()
        kwargs.update({'current_org_pk': self.object.organization.pk})
        return kwargs

    def _check_access_perms(self, user):
        organization_pk = self.kwargs.get('pk')
        if not Organization.objects.get(pk=organization_pk).is_owner(user):
            return HttpResponseForbidden(_("Sorry, owners only"))

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        self.object = self.get_object()
        response = self._check_access_perms(request.user)
        if response is not None:
            return response
        return super(ChangeOwnerView, self).dispatch(
            request, *args, **kwargs)

