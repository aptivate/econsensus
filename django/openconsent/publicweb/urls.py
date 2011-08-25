from django.conf.urls.defaults import patterns, url
from publicweb.views import add_decision, edit_decision, decision_list
from publicweb.models import Decision

from django.views.generic.list_detail import object_detail
from publicweb.views import export_csv

urlpatterns = patterns('openconsent.publicweb.views',
    url(r'^export_csv/$',
        export_csv,
        name='export_csv'),
    url(r'^add/$',
        add_decision,
        name='add_decision'),
    url(r'^edit/(?P<decision_id>[\d]+)/$', 
        edit_decision,
        name='edit_decision'),
    url(r'^view/(?P<object_id>[\d]+)/$',
        object_detail,
        { 'queryset': Decision.objects.all(),
         'template_name': 'decision_detail.html'},
        name='view_decision'),
    url(r'^decision_list/$',
        decision_list,
        name='decision_list')
    )

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^login/',
        'login', name='login'),
    url(r'^logout/',
        'logout', {'template_name':'registration/logout.html'}, name='logout'),
)
