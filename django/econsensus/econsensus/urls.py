from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.core.urlresolvers import reverse_lazy
from organizations.backends import invitation_backend
from registration.forms import RegistrationFormUniqueEmail
from custom_auth.forms import CustomAuthenticationForm, CustomPasswordResetForm
from registration.backends.default.views import RegistrationView
from custom_organizations.forms import CustomUserSignupRegistrationForm

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
    url(r'', include('publicweb.urls')),
)

urlpatterns += patterns('',
    url(r'^accounts/register/$', RegistrationView.as_view(
        form_class = CustomUserSignupRegistrationForm,
        template_name = 'organizations/register_form.html'), 
        name = 'registration_register'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        {'authentication_form': CustomAuthenticationForm}),
    url(r'^accounts/password/reset/$', 'django.contrib.auth.views.password_reset',
        {'password_reset_form': CustomPasswordResetForm}),
    url(r'^accounts/', include('registration.backends.default.urls')),

)

