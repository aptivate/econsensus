from django.conf.urls.defaults import patterns, url
from django.views.generic.list_detail import object_detail
from django.views.generic.simple import redirect_to

from views import add_decision, add_decision_status, edit_decision, listing, \
                     export_csv, inline_edit_decision, view_decision
from models import Decision

urlpatterns = patterns('openconsent.publicweb.views',
    url(r'^export_csv/$',
        export_csv,
        name='publicweb_export_csv'),
    url(r'^add/$',
        add_decision,
        name='publicweb_decision_add'),
    url(r'^add/(?P<status_id>[\d]+)/$',
        add_decision_status,
        name='publicweb_decision_add_status'),
    url(r'^edit/(?P<decision_id>[\d]+)/$', 
        edit_decision,
        name='publicweb_decision_edit'),
    url(r'^view/(?P<decision_id>[\d]+)/$',
        view_decision,
        name='view_decision'),                       
    url(r'^view/(?P<decision_id>[\d]+)/snippet/$',
        view_decision,
        { 'template_name': 'decision_detail_snippet.html'},
        name='view_decision_snippet'),
    url(r'^view/(?P<decision_id>[\d]+)/form/$',
        inline_edit_decision,
        { 'template_name': 'decision_detail_form.html'},
        name='inline_edit_decision_form'),
    url(r'^view/(?P<decision_id>[\d]+)/edit/$',
        inline_edit_decision,
        name='inline_edit_decision'),
    url(r'^list/(?P<status>[a-z]+)/$',
        listing,
        name='list'),
    url(r'^$', redirect_to, {'url': 'list/proposal/'}),
    )
