from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from organizations.models import Organization
from organizations.admin import OrganizationAdmin

# With django-guardian object permissions support
class GuardedOrganizationAdmin(OrganizationAdmin, GuardedModelAdmin):
    pass

admin.site.unregister(Organization)
admin.site.register(Organization, GuardedOrganizationAdmin)
