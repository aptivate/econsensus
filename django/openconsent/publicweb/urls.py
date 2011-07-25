from django.conf.urls.defaults import patterns, url
from publicweb.views import add_decision, edit_decision, decision_list

urlpatterns = patterns('openconsent.publicweb.views',
    url(r'^add/$',
        add_decision,
        name='add_decision'),
    url(r'^edit/(?P<decision_id>[\d]+)/$', 
        edit_decision,
        name='edit_decision'),
    url(r'^list/$',
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