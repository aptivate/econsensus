from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_list

import openconsent.publicweb.views

urlpatterns = patterns('openconsent.publicweb.views',
    url(r'^scorecard/partner/(?P<agency_name>[-\w ]+)/$',
        openconsent.publicweb.views.home_page),
    url(r'^decision/add$',
        openconsent.publicweb.views.decision_add_page),
    url(r'^decision/(?P<decision_id>[\d]+)/$',
        openconsent.publicweb.views.decision_view_page),
)