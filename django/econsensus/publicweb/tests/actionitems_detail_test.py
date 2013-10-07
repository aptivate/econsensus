from django.test.client import RequestFactory
from django_dynamic_fixture import G
from django.contrib.auth.models import AnonymousUser
from waffle import Switch

from actionitems.models import ActionItem

from publicweb.views import EconsensusActionitemDetailView
from publicweb.tests.decision_test_case import DecisionTestCase


class ActionitemsDetailTest(DecisionTestCase):

    def setUp(self):
        # ensure the waffle stuff is set up
        Switch.objects.create(name='actionitems', active=True)
        super(ActionitemsDetailTest, self).setUp()

    def tearDown(self):
        Switch.objects.all().delete()
        super(ActionitemsDetailTest, self).tearDown()

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
