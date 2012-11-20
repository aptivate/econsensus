from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required
from views import CustomOrganizationUserUpdate

urlpatterns = patterns('',    
    # Use custom urganization user URLs
#    url(r'^(?P<organization_pk>[\d]+)/people/add/$',
#        view=login_required(OrganizationUserCreate.as_view()),
#        name="organization_user_add"),
    url(r'^(?P<organization_pk>[\d]+)/people/(?P<user_pk>[\d]+)/edit/$',
        view=login_required(CustomOrganizationUserUpdate.as_view()),
        name="organization_user_edit"),
)