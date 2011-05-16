from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_list

import openconsent.publicweb.views

urlpatterns = patterns('openconsent.publicweb.views',
    url(r'^decision/add$',
        openconsent.publicweb.views.decision_add_page),
    url(r'^decision/(?P<decision_id>[\d]+)/$',
        openconsent.publicweb.views.decision_view_page),
    url(r'^decision_list/(?P<decisionlist_id>[\d]+)/$',
        openconsent.publicweb.views.decision_list, name='decision_list'),
    url(r'^decision_lists/$',
        openconsent.publicweb.views.decision_lists),
)