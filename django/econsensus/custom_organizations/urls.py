from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required
from views import CustomOrganizationCreate, \
                    CustomOrganizationUpdate,\
                    CustomOrganizationUserCreate,\
                    CustomOrganizationUserUpdate,\
                    CustomOrganizationUserDelete,\
                    CustomOrganizationUserRemind, \
                    CustomOrganizationUserList

urlpatterns = patterns('',    
    # Use custom urganization user URLs
    url(r'^add/$', view=login_required(CustomOrganizationCreate.as_view()),
        name="organization_add"),
    url(r'^(?P<organization_pk>[\d]+)/edit/$',
        view=login_required(CustomOrganizationUpdate.as_view()),
        name="organization_edit"),
    url(r'^(?P<organization_pk>[\d]+)/people/add/$',
        view=login_required(CustomOrganizationUserCreate.as_view()),
        name="organization_user_add"),
    url(r'^(?P<organization_pk>[\d]+)/people/(?P<user_pk>[\d]+)/edit/$',
        view=login_required(CustomOrganizationUserUpdate.as_view()),
        name="organization_user_edit"),
    url(r'^(?P<organization_pk>[\d]+)/people/(?P<user_pk>[\d]+)/delete/$',
        view=login_required(CustomOrganizationUserDelete.as_view()),
        name="organization_user_delete"),                       
    url(r'^(?P<organization_pk>[\d]+)/people/(?P<user_pk>[\d]+)/remind/$',
        view=login_required(CustomOrganizationUserRemind.as_view()),
        name="organization_user_remind"),
    url(r'^(?P<organization_pk>[\d]+)/people/$',
        view=login_required(CustomOrganizationUserList.as_view()),
        name="organization_user_list"),
    url(r'', include('organizations.urls')),
)
