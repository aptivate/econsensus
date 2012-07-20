from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from registration.forms import RegistrationFormUniqueEmail
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls), name='admin'),
    url(r'^settings/', include('livesettings.urls')),
    url(r'', include('openconsent.publicweb.urls')),    
    )

urlpatterns += patterns('',
    url(r'^accounts/register/$', 'registration.views.register',
        {'form_class':RegistrationFormUniqueEmail,
        'backend':'registration.backends.default.DefaultBackend' }, name='registration_register'),                        
    )

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^accounts/', include('registration.backends.default.urls')),
)

if settings.DEBUG == True:
    urlpatterns += patterns('',
    
        url(r'^site_media/(?P<path>.*)$',
            'django.views.static.serve',
            { 'document_root' : settings.MEDIA_ROOT })
    )
