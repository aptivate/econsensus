from django.conf.urls.defaults import patterns, url
from django.views.generic.list_detail import object_detail
from django.views.generic.simple import redirect_to

from views import add_decision, edit_decision, listing, \
                     export_csv
from models import Decision

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
    url(r'^list/(?P<status>[a-z]+)/$',
        listing,
        name='list'),
    url(r'^$', redirect_to, {'url': 'list/proposal/'}),
    )