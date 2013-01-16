from django.utils.unittest import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse, resolve
from django.contrib.auth.models import User

from decision_test_case import DecisionTestCase

from publicweb.views import EconsensusActionitemCreateView
from organizations.models import Organization
from actionitems.models import ActionItem
from actionitems.forms import ActionItemCreateForm

from BeautifulSoup import BeautifulSoup


class ActionitemsViewTestFast(TestCase):

    def test_create_model(self):
        assert EconsensusActionitemCreateView.model == ActionItem

    def test_create_formclass(self):
        assert EconsensusActionitemCreateView.form_class == ActionItemCreateForm

    def test_create_template(self):
        assert EconsensusActionitemCreateView.template_name == 'actionitem_update_page.html'

    def test_get_successurl(self):
        createview = EconsensusActionitemCreateView()
        createview.kwargs = {'pk' : 1}
        assert createview.get_success_url() == reverse('publicweb_item_detail', kwargs={'pk': 1})

    def test_get_origin(self):
        # Have get_origin get the pk from url
        createview = EconsensusActionitemCreateView()
        createview.kwargs = {'pk' : 1}
        origin = createview.get_origin(RequestFactory())
        assert origin == 1

    def test_login_and_editor_not_logged_in(self):
        get_request = RequestFactory().get('/')
        user = User.objects.create()
        user.is_authenticated = lambda: False
        get_request.user = user
        response = EconsensusActionitemCreateView.as_view()(get_request, pk=1)
        assert response.status_code == 302  # Redirects to login

    def test_create_url(self):
        resolved = resolve(reverse('actionitem_create', kwargs={'pk': 1}))
        assert resolved.func.func_name == 'EconsensusActionitemCreateView'

# Untested:
# - item_detail template



class ActionitemsViewTest(DecisionTestCase):

    def test_login_and_editor(self):
        decision = self.create_and_return_decision()
        get_request = RequestFactory().get('/')
        get_request.user = self.betty
        response = EconsensusActionitemCreateView.as_view()(get_request, pk=decision.pk)
        assert response.status_code == 200

    def test_login_and_editor_noeditor_perms(self):
        decision = self.create_and_return_decision()
        get_request = RequestFactory().get('/')
        assert self.charlie.is_authenticated()  # Confirm user is logged in
        get_request.user = self.charlie
        response = EconsensusActionitemCreateView.as_view()(get_request, pk=decision.pk)
        assert response.status_code == 403

    def test_render_and_confirm_origin_and_other_required_fields(self):
        decision = self.create_and_return_decision()
        get_request = RequestFactory().get('/')
        get_request.user = self.betty
        response = EconsensusActionitemCreateView.as_view()(get_request, pk=decision.pk)
        response.render()
        soup = BeautifulSoup(str(response.content))
        origin = soup.find("input", {"id": "id_origin"})
        assert origin['value'] == str(decision.pk)
        assert soup.find("textarea", {"id": "id_description"})
        assert soup.find("input", {"id": "id_responsible"})

