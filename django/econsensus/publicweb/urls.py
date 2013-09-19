from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView

from views import (DecisionCreate, DecisionUpdate, DecisionDetail, DecisionList,
                    ExportCSV, FeedbackCreate, FeedbackSnippetCreate, 
                    FeedbackUpdate, EconsensusActionitemCreateView, 
                    EconsensusActionitemUpdateView,
                    EconsensusActionitemListView, OrganizationRedirectView,
                    YourDetails, UserNotificationSettings, 
                    EconsensusActionitemDetailView, DecisionSearchView)

from models import Feedback
 

urlpatterns = patterns('econsensus.publicweb.views',
    url(r'^user_settings/your_details/$',
        YourDetails.as_view(),
        name='your_details'),
    url(r'^user_settings/notification_settings/(?P<organization>[\d]+)/$',
        UserNotificationSettings.as_view(), name='notification_settings'),

    url(r'^(?P<org_slug>[-\w]+)/export_csv/$',
        ExportCSV.as_view(),
        name='publicweb_export_csv'),

    #Feedback urls...
    url(r'^feedback/create/(?P<parent_pk>[\d]+)/$', 
        FeedbackCreate.as_view(template_name = 'feedback_update_page.html'),
        name='publicweb_feedback_create'),
    url(r'^feedback/update/(?P<pk>[\d]+)/$', 
        FeedbackUpdate.as_view(template_name = 'feedback_update_page.html'),
        name='publicweb_feedback_update'),
    url(r'^feedback/detail/(?P<pk>[\d]+)/$', 
        login_required(DetailView.as_view(
            model = Feedback,
            template_name = 'feedback_detail_page.html')),
        name='publicweb_feedback_detail'),
    #snippets
    url(r'^feedback/create/snippet/(?P<parent_pk>[\d]+)/$', 
        FeedbackSnippetCreate.as_view(
        template_name='feedback_update_snippet.html'),
        name='publicweb_feedback_snippet_create'),
    url(r'^feedback/update/snippet/(?P<pk>[\d]+)/$', 
        FeedbackUpdate.as_view(template_name = 'feedback_update_snippet.html'),
        name='publicweb_feedback_snippet_update'),
    url(r'^feedback/detail/snippet/(?P<pk>[\d]+)/$', 
        login_required(DetailView.as_view(
            model = Feedback,
            template_name = 'feedback_detail_snippet.html')),
        name='publicweb_feedback_snippet_detail'),

    #decision urls...
    url(r'^(?P<org_slug>[-\w]+)/decision/create/(?P<status>[a-z]+)/$',
        DecisionCreate.as_view(template_name = 'decision_update_page.html' ),
        name='publicweb_decision_create'),
    url(r'^decision/update/(?P<pk>[\d]+)/$',
        DecisionUpdate.as_view(template_name = 'decision_update_page.html'),
        name='publicweb_decision_update'),    
    url(r'^decision/detail/(?P<pk>[\d]+)/$',
        DecisionDetail.as_view(template_name = 'decision_detail_page.html'),
        name='publicweb_decision_detail'),
    #snippets    
    url(r'^(?P<org_slug>[-\w]+)/decision/create/snippet/(?P<status>[a-z]+)/$',
        DecisionCreate.as_view(template_name = 'decision_update_snippet.html'),
        name='publicweb_decision_snippet_create'),
    url(r'^decision/update/snippet/(?P<pk>[\d]+)/$',
        DecisionUpdate.as_view(template_name = 'decision_update_snippet.html'),
        name='publicweb_decision_snippet_update'),    
    url(r'^decision/detail/snippet/(?P<pk>[\d]+)/$',
        DecisionDetail.as_view(template_name = 'decision_detail_snippet.html'),
        name='publicweb_decision_snippet_detail'),                       

    #item urls
    url(r'^item/detail/(?P<pk>[\d]+)/$',
        DecisionDetail.as_view(template_name = 'item_detail.html'),
        name='publicweb_item_detail'),                       
    url(r'^(?P<org_slug>[-\w]+)/item/list/(?P<status>[a-z]+)/$',
        DecisionList.as_view(template_name='decision_list.html'),
        name='publicweb_item_list'),
    url(r'^(?P<org_slug>[-\w]+)/search/$',
        DecisionSearchView.make(),
        name='publicweb_decision_search'),

    #actionitem urls
    url(r'^item/detail/(?P<pk>[\d]+)/actionitem/add/$', 
        EconsensusActionitemCreateView.as_view(), 
        name='actionitem_create'),
    url(r'^item/detail/(?P<decisionpk>[\d]+)/actionitem/(?P<pk>[\d]+)/$',
        EconsensusActionitemDetailView.as_view(), 
        name='actionitem_detail'),                   
    url(r'^item/detail/(?P<decisionpk>[\d]+)/actionitem/(?P<pk>[\d]+)/update/$',
        EconsensusActionitemUpdateView.as_view(), 
        name='actionitem_update'),
    url(r'^(?P<org_slug>[-\w]+)/actionitem/list/$',
        EconsensusActionitemListView.as_view(), 
        name='actionitem_list'),

    url(r'^(?P<org_slug>[-\w]+)/item/list/$',
        DecisionList.as_view(template_name='decision_list.html'),
        name='publicweb_default_item_list'),
    url(r'^$', 
        OrganizationRedirectView.as_view(),
        name='publicweb_root'),
    )
