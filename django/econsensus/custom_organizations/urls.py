from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required
from views import CustomOrganizationUserCreate,\
                    CustomOrganizationUserUpdate,\
                    CustomOrganizationUserDelete, \
                    CustomOrganizationList

urlpatterns = patterns('',    
    # Use custom urganization user URLs
    url(r'^(?P<organization_pk>[\d]+)/people/add/$',
        view=login_required(CustomOrganizationUserCreate.as_view()),
        name="organization_user_add"),
    url(r'^(?P<organization_pk>[\d]+)/people/(?P<user_pk>[\d]+)/edit/$',
        view=login_required(CustomOrganizationUserUpdate.as_view()),
        name="organization_user_edit"),
    url(r'^(?P<organization_pk>[\d]+)/people/(?P<user_pk>[\d]+)/delete/$',
        view=login_required(CustomOrganizationUserDelete.as_view()),
        name="organization_user_delete"),
    url(r'^$', view=login_required(CustomOrganizationList.as_view()),
        name="organization_list"),
    url(r'', include('organizations.urls')),
)