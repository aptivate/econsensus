from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.core.urlresolvers import reverse_lazy
from organizations.backends import invitation_backend
from registration.forms import RegistrationFormUniqueEmail

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/logout/$', 'django.contrib.auth.views.logout_then_login',
        {'login_url': reverse_lazy('admin:index')}),
    url(r'^admin/', include(admin.site.urls), name='admin'),
    url(r'^settings/', include('livesettings.urls')),
    url(r'^notification/', include('notification.urls')),
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^organizations/', include('custom_organizations.urls')),
    url(r'^invitations/', include(invitation_backend().get_urls())),
    url(r'', include('econsensus.publicweb.urls')),
)

urlpatterns += patterns('',
    url(r'^accounts/register/$', 'registration.views.register',
        {'form_class':RegistrationFormUniqueEmail,
        'backend':'registration.backends.default.DefaultBackend' }, name='registration_register'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
    url(r'^accounts/', include('registration.backends.default.urls')),

)

urlpatterns += staticfiles_urlpatterns()
