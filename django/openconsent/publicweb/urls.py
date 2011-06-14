from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_list
from django.conf import settings

import openconsent.publicweb.views

urlpatterns = patterns('openconsent.publicweb.views',
    url(r'^decision/add$', 'decision_add_page', name='decision_add'),
    url(r'^decision/(?P<decision_id>[\d]+)/$', 'decision_view_page',
        name='decision_edit'),
    url(r'^decision_list/$',
        'decision_list', name='decision_list')
    )

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^login/',
        'login', name='login'),
)