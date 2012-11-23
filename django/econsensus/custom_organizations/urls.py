from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required
from views import CustomOrganizationUserCreate, CustomOrganizationUserUpdate 

urlpatterns = patterns('',    
    # Use custom urganization user URLs
    url(r'^(?P<organization_pk>[\d]+)/people/add/$',
        view=login_required(CustomOrganizationUserCreate.as_view()),
        name="organization_user_add"),
    url(r'^(?P<organization_pk>[\d]+)/people/(?P<user_pk>[\d]+)/edit/$',
        view=login_required(CustomOrganizationUserUpdate.as_view()),
        name="organization_user_edit"),
    url(r'', include('organizations.urls')),
)