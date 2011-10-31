from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #url(r'^public/', include('openconsent.publicweb.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls), name='admin'),
    url(r'', include('openconsent.publicweb.urls')),    
    )

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^accounts/login/',
        'login', name='login'),
    url(r'^accounts/logout/',
        'logout_then_login', name='logout'),
)

if settings.DEBUG == True:
    urlpatterns += patterns('',
    
        url(r'^site_media/(?P<path>.*)$',
            'django.views.static.serve',
            { 'document_root' : settings.MEDIA_ROOT })
    )