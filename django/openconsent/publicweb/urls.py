from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import redirect_to
from django.views.generic.list_detail import object_detail
from django.contrib.auth.decorators import login_required

from views import new, modify, listing, \
                     export_csv, inline_modify_decision

from models import Decision

#is it useful to have the status id in the URL? Seems not to me. -pcb

decision_info = {
    'queryset': Decision.objects.all(),
    'template_name': 'decision_detail.html'
}

decision_snippet_info = {
    'queryset': Decision.objects.all(),
    'template_name': 'decision_detail_snippet.html'
}
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
    url(r'^view/(?P<object_id>[\d]+)/$',
        login_required(object_detail),
        decision_info,
        name='publicweb_decision_view'),                       
    url(r'^view/(?P<object_id>[\d]+)/snippet/$',
        login_required(object_detail),
        decision_snippet_info,
        name='publicweb_decision_view_snippet'),
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
