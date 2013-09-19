from django.shortcuts import get_object_or_404

from custom_organizations.models import Group

class GroupMixin(object):
    group_model = Group
    group_context_name = 'group'

    def get_object(self):
        if hasattr(self, 'group'):
            return self.group
        group_pk = self.kwargs.get('group_pk', None)
        self.group = get_object_or_404(self.group_model, pk = group_pk)
        return self.group
