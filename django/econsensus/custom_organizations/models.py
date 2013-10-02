from django import forms
from django.db import models

from organizations.models import OrganizationUser, Organization
from django.utils.translation import ugettext_lazy as _

class Group(models.Model):
    name = models.CharField(max_length=200,
            help_text=_("The name of the Group"))
    organization = models.ForeignKey(Organization,
            related_name="organization_groups")
    members = models.ManyToManyField(OrganizationUser)
    owner = models.ForeignKey(OrganizationUser,
        related_name="organizationuser_groupowner")

    class Meta:
        ordering = ['name']
        verbose_name = _("group")
        verbose_name_plural = _("groups")

    def __unicode__(self):
        return self.name
