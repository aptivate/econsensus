from publicweb.tests.decision_test_case import DecisionTestCase
from django.test.client import RequestFactory
from publicweb.views import EconsensusActionitemDetailView,\
    EconsensusActionitemCreateView, EconsensusActionitemUpdateView
from django_dynamic_fixture import G
from actionitems.models import ActionItem
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse

class ActionitemsDetailTest(DecisionTestCase):
    def test_action_item_detail_view_uses_action_item_detail_snippet_template(self):
        actionitem = G(ActionItem)
        get_request = RequestFactory().get('/')
        get_request.user = self.betty
        response = EconsensusActionitemDetailView.as_view()(get_request, pk=actionitem.pk)
        self.assertIn('actionitem_detail_snippet.html', response.template_name)
        actionitem.delete()
    
    def test_action_item_detail_view_doesnt_use_item_detail_template(self):
        actionitem = G(ActionItem)
        get_request = RequestFactory().get('/')
        get_request.user = self.betty
        response = EconsensusActionitemDetailView.as_view()(get_request, pk=actionitem.pk)
        self.assertNotIn('item_detail.html', response.template_name)
        actionitem.delete()
    
    def test_login_required_to_access_view(self):
        actionitem = G(ActionItem)
        get_request = RequestFactory().get('/')
        get_request.user = AnonymousUser()
        response = EconsensusActionitemDetailView.as_view()(get_request, pk=actionitem.pk)
        self.assertEqual(response.status_code, 302)
        actionitem.delete()