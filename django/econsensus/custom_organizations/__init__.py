import organizations
from organizations.models import OrganizationOwner

from monkeypatch import insert


@insert(organizations.models.OrganizationUser, 'is_owner')
def is_owner(self):
    return OrganizationOwner.objects.filter(organization=self.organization) \
        .filter(organization_user_id=self.id).exists()


@insert(organizations.models.OrganizationUser, 'is_editor')
def is_editor(self):
    return self.user.has_perm('edit_decisions_feedback', self.organization)


@insert(organizations.models.OrganizationUser, 'get_role')
def get_role(self):
    """ Method to be monkeypatched into OrganizationUser so we know what
    sort of user they are - owner, admin, editor or viewer """
    if self.is_owner():
        return 'owner'
    elif self.is_admin:  # is_admin is a field, not a method
        return 'admin'
    elif self.is_editor():
        return 'editor'
    else:
        return 'viewer'
