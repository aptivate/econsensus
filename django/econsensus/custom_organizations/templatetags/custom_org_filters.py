from django import template
from custom_organizations.models import Group

register = template.Library()

@register.filter
def get_organization_groups_for_current_user(org, user):
    return Group.objects.filter(organization=org, members__user=user)

@register.filter
def is_member_of_group(group, user): 
    result = Group.objects.filter(id=group.id, members__user=user)
    return result

@register.filter
def is_group_owner(group, user):
    return group.owner.user == user

@register.filter
def get_organization_groups(org):
    return Group.objects.filter(organization=org)