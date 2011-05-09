from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_list

import openconsent.publicweb.views

urlpatterns = patterns('openconsent.publicweb.views',
    url(r'^scorecard/partner/(?P<agency_name>[-\w ]+)/$',
        openconsent.publicweb.views.home_page,
        name='public-agency-scorecard'),
)