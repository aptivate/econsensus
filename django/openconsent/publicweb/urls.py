from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_list

import openconsent.publicweb.views

urlpatterns = patterns('openconsent.publicweb.views',
    url(r'^decision/add$', 'decision_add_page', name='decision_add'),
    url(r'^decision/(?P<decision_id>[\d]+)/$', 'decision_view_page',
        name='decision_edit'),
    url(r'^decision_list/(?P<group_id>[\d]+)/$',
        openconsent.publicweb.views.decision_list, name='decision_list'),
    url(r'^groups/$',
        openconsent.publicweb.views.groups, name='groups'),
    url(r'^group_add/$', 'group_add', name='group_add'),
)