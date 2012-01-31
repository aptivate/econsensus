from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import redirect_to
from django.views.generic.list_detail import object_detail
from django.contrib.auth.decorators import login_required

from views import create_decision, update_decision, object_list_by_status, \
                     export_csv, create_feedback, \
                     update_feedback

from models import Decision, Feedback

decision_detail_info = {
    'queryset': Decision.objects.all(),
    'template_name': 'decision_detail_page.html'
}

decision_update_info = {
    'template_name': 'decision_update_page.html'
}

decision_create_info = {
    'template_name': 'decision_update_page.html'
}

decision_detail_snippet_info = {
    'queryset': Decision.objects.all(),
    'template_name': 'decision_detail_snippet.html'
}

decision_update_snippet_info = {
    'template_name': 'decision_update_snippet.html'
}

decision_create_snippet_info = {
    'template_name': 'decision_update_snippet.html'
}

item__detail_info = {
    'queryset': Decision.objects.all(),
    'template_name': 'item_detail.html'
}

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
        login_required(object_detail),
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
        login_required(object_detail),
        feedback_snippet_detail_info,
        name='publicweb_feedback_snippet_detail'),

    #decision urls...
    url(r'^decision/create/(?P<status_id>[\d]+)/$',
        create_decision,
        decision_create_info,
        name='publicweb_decision_create'),
    url(r'^decision/update/(?P<object_id>[\d]+)/$',
        update_decision,
        decision_update_info,        
        name='publicweb_decision_update'),    
    url(r'^decision/detail/(?P<object_id>[\d]+)/$',
        login_required(object_detail),
        decision_detail_info,
        name='publicweb_decision_detail'),
    #snippets                       
    url(r'^decision/create/snippet/(?P<status_id>[\d]+)/$',
        create_decision,
        decision_create_snippet_info,
        name='publicweb_decision_snippet_create'),
    url(r'^decision/update/snippet/(?P<object_id>[\d]+)/$',
        update_decision,
        decision_update_snippet_info,
        name='publicweb_decision_snippet_update'),    
    url(r'^decision/detail/snippet/(?P<object_id>[\d]+)/$',
        login_required(object_detail),
        decision_detail_snippet_info,
        name='publicweb_decision_snippet_detail'),                       

    #item urls
    url(r'^item/detail/(?P<object_id>[\d]+)/$',
        login_required(object_detail),
        item__detail_info,
        name='publicweb_item_detail'),                       
    url(r'^item/list/(?P<status_text>[a-z]+)/$',
        object_list_by_status,
        name='publicweb_item_list'),

    url(r'^$', redirect_to, {'url': 'item/list/proposal/'}),
    )
