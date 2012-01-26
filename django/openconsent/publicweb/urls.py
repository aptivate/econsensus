from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import redirect_to
from django.views.generic.list_detail import object_detail
from django.contrib.auth.decorators import login_required

from views import create_decision, update_decision, object_list_by_status, \
                     export_csv, inline_modify_decision, create_feedback, \
                     update_feedback

from models import Decision, Feedback

from forms import DecisionForm

#is it useful to have the status id in the URL? Seems not to me. -pcb
new_decision_info = {
    'queryset': Decision.objects.all(),
    'template_name': 'decision_detail2.html'
}

item_info = {
    'queryset': Decision.objects.all(),
    'template_name': 'item_detail.html'
}

decision_info = {
    'queryset': Decision.objects.all(),
    'template_name': 'decision_detail.html'
}

decision_create_info = {
    'model': Decision,
    'form_class' : DecisionForm,
    'template_name': 'decision_form2.html'
}

decision_snippet_info = {
    'queryset': Decision.objects.all(),
    'template_name': 'decision_detail_snippet.html'
}

feedback_detail_info = {
    'queryset': Feedback.objects.all(),
    'template_name': 'feedback_detail_page.html'
}

feedback_edit_info = {'model' : Feedback,
                      'template_name': 'feedback_form_page.html'
}

feedback_create_info = {'model' : Decision,
                        'template_name': 'feedback_form_page.html'}

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
        feedback_edit_info,
        name='publicweb_feedback_update'),
    url(r'^feedback/detail/(?P<object_id>[\d]+)/$', 
        login_required(object_detail),
        feedback_detail_info,
        name='publicweb_feedback_detail'),
                       
    #decision urls...
    url(r'^decision/create/(?P<status_id>[\d]+)/$',
        create_decision,
        name='publicweb_decision_create'),
    url(r'^decision/update/(?P<object_id>[\d]+)/$',
        update_decision,
        name='publicweb_decision_update'),    
    url(r'^decision/detail/(?P<object_id>[\d]+)/$',
        login_required(object_detail),
        new_decision_info,
        name='publicweb_decision_detail'),                       

    #item urls
    url(r'^item/detail/(?P<object_id>[\d]+)/$',
        login_required(object_detail),
        item_info,
        name='publicweb_item_detail'),                       
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

    url(r'^item/list/(?P<status>[a-z]+)/$',
        object_list_by_status,
        name='list'),

    url(r'^$', redirect_to, {'url': 'item/list/proposal/'}),
    )
