from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import redirect_to
from django.contrib.auth.decorators import login_required
from django.views.generic import list_detail
from django.core.urlresolvers import reverse

from views import create_decision, update_decision, \
                    decision_detail, object_list_by_status, \
                    export_csv, create_feedback, \
                    update_feedback, redirect_to_proposal_list

from models import Decision, Feedback

feedback_detail_info = {'queryset': Feedback.objects.all(),
                        'template_name': 'feedback_detail_page.html'
}

feedback_update_info = {'model' : Feedback,
                        'template_name': 'feedback_update_page.html'
}

feedback_create_info = {'model' : Decision,
                        'template_name': 'feedback_update_page.html'}

feedback_snippet_detail_info = {'queryset': Feedback.objects.all(),
                                'template_name': 'feedback_detail_snippet.html'
}

feedback_snippet_update_info = {'model' : Feedback,
                                'template_name': 'feedback_update_snippet.html'
}

feedback_snippet_create_info = {'model' : Decision,
                                'snippet_template': 'feedback_detail_snippet.html',
                                'template_name': 'feedback_update_snippet.html'}

urlpatterns = patterns('openconsent.publicweb.views',
    url(r'^export_csv/$',
        export_csv,
        name='publicweb_export_csv'),
                       
    #Feedback urls...
    url(r'^feedback/create/(?P<object_id>[\d]+)/$', 
        create_feedback,
        feedback_create_info,
        name='publicweb_feedback_create'),
    url(r'^feedback/update/(?P<object_id>[\d]+)/$', 
        update_feedback,
        feedback_update_info,
        name='publicweb_feedback_update'),
    url(r'^feedback/detail/(?P<object_id>[\d]+)/$', 
        login_required(list_detail.object_detail),
        feedback_detail_info,
        name='publicweb_feedback_detail'),
    #snippets
    url(r'^feedback/create/snippet/(?P<object_id>[\d]+)/$', 
        create_feedback,
        feedback_snippet_create_info,
        name='publicweb_feedback_snippet_create'),
    url(r'^feedback/update/snippet/(?P<object_id>[\d]+)/$', 
        update_feedback,
        feedback_snippet_update_info,
        name='publicweb_feedback_snippet_update'),
    url(r'^feedback/detail/snippet/(?P<object_id>[\d]+)/$', 
        login_required(list_detail.object_detail),
        feedback_snippet_detail_info,
        name='publicweb_feedback_snippet_detail'),

    #decision urls...
    url(r'^decision/create/(?P<status>[a-z]+)/$',
        create_decision,
        { 'template_name': 'decision_update_page.html' },
        name='publicweb_decision_create'),
    url(r'^decision/update/(?P<object_id>[\d]+)/$',
        update_decision,
        { 'template_name': 'decision_update_page.html'},
        name='publicweb_decision_update'),    
    url(r'^decision/detail/(?P<object_id>[\d]+)/$',
        decision_detail,
        { 'template_name': 'decision_detail_page.html' },
        name='publicweb_decision_detail'),
    #snippets                       
    url(r'^decision/create/snippet/(?P<status>[a-z]+)/$',
        create_decision,
        {'template_name': 'decision_update_snippet.html'},
        name='publicweb_decision_snippet_create'),
    url(r'^decision/update/snippet/(?P<object_id>[\d]+)/$',
        update_decision,
        {'template_name': 'decision_update_snippet.html'},
        name='publicweb_decision_snippet_update'),    
    url(r'^decision/detail/snippet/(?P<object_id>[\d]+)/$',
        login_required(decision_detail),
        { 'template_name': 'decision_detail_snippet.html' },
        name='publicweb_decision_snippet_detail'),                       

    #item urls
    url(r'^item/detail/(?P<object_id>[\d]+)/$',
        decision_detail,
        {'template_name': 'item_detail.html'},
        name='publicweb_item_detail'),                       
    url(r'^item/list/(?P<status>[a-z]+)/$',
        object_list_by_status,
        {'template_name': 'decision_list.html'},
        name='publicweb_item_list'),
    url(r'^$', redirect_to_proposal_list)
    )
