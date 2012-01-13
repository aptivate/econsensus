from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import redirect_to

from views import new, modify, listing, \
                     export_csv, inline_modify_decision, view_decision

#is it useful to have the status id in the URL? Seems not to me. -pcb

urlpatterns = patterns('openconsent.publicweb.views',
    url(r'^export_csv/$',
        export_csv,
        name='publicweb_export_csv'),
    url(r'^add/(?P<status_id>[\d]+)/$',
        new,
        name='publicweb_decision_new'),
    url(r'^edit/(?P<decision_id>[\d]+)/$', 
        modify,
        name='publicweb_decision_modify'),
    url(r'^view/(?P<decision_id>[\d]+)/$',
        view_decision,
        name='view_decision'),                       
    url(r'^view/(?P<decision_id>[\d]+)/snippet/$',
        view_decision,
        { 'template_name': 'decision_detail_snippet.html'},
        name='view_decision_snippet'),
    url(r'^view/(?P<decision_id>[\d]+)/form/$',
        inline_modify_decision,
        { 'template_name': 'decision_detail_form.html'},
        name='inline_edit_decision_form'),
    url(r'^view/(?P<decision_id>[\d]+)/edit/$',
        inline_modify_decision,
        name='inline_edit_decision'),
    url(r'^list/(?P<status>[a-z]+)/$',
        listing,
        name='list'),

    url(r'^$', redirect_to, {'url': 'list/proposal/'}),
    )
