from django.conf.urls.defaults import patterns, url

from openconsent.publicweb.views import decision_add_page, decision_view_page, decision_list

urlpatterns = patterns('openconsent.publicweb.views',
    url(r'^decision/add$',
        decision_add_page,
        name='decision_add'),
    url(r'^decision/(?P<decision_id>[\d]+)/$', 
        decision_view_page,
        name='decision_edit'),
    url(r'^decision_list/$',
        decision_list,
        name='decision_list'),
    url(r'^$',
        decision_list,
        name='decision_list')
    )

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^login/',
        'login', name='login'),
    url(r'^logout/',
        'logout', {'template_name':'registration/logout.html'}, name='logout'),
)