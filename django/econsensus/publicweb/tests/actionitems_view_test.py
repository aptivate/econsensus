from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse, resolve
from django.test.client import RequestFactory
from django.utils.unittest import TestCase
from BeautifulSoup import BeautifulSoup
from waffle import Switch

from decision_test_case import DecisionTestCase

from actionitems.models import ActionItem
from notification import models as notifications
from signals.management import ACTIONITEM_NEW, ACTIONITEM_CHANGE

from publicweb.forms import (EconsensusActionItemCreateForm,
                             EconsensusActionItemUpdateForm)
from publicweb.views import (EconsensusActionitemCreateView,
                             EconsensusActionitemUpdateView,
                             EconsensusActionitemListView)


class ActionitemsViewTestFast(TestCase):

    def setUp(self):
        # ensure the waffle stuff is set up
        Switch.objects.create(name='actionitems', active=True)
        super(ActionitemsViewTestFast, self).setUp()

    def tearDown(self):
        Switch.objects.all().delete()
        super(ActionitemsViewTestFast, self).tearDown()

    def test_create_model(self):
        assert EconsensusActionitemCreateView.model == ActionItem

    def test_create_formclass(self):
        assert EconsensusActionitemCreateView.form_class == EconsensusActionItemCreateForm

    def test_create_template(self):
        assert EconsensusActionitemCreateView.template_name == 'actionitem_create_snippet.html'

    def test_update_model(self):
        assert EconsensusActionitemUpdateView.model == ActionItem

    def test_update_formclass(self):
        assert EconsensusActionitemUpdateView.form_class == EconsensusActionItemUpdateForm

    def test_update_template(self):
        assert EconsensusActionitemUpdateView.template_name == 'actionitem_update_snippet.html'

    def test_update_form_kwargs_contain_prefix(self):
        updateview = EconsensusActionitemUpdateView()
        updateview.object = ActionItem(id=1)
        updateview.request = RequestFactory().get('/')
        updateview.kwargs = {'decisionpk': 1}
        form_kwargs = updateview.get_form_kwargs()
        assert 'prefix' in form_kwargs
        assert form_kwargs['prefix'] == "actionitem-1"

    def test_create_get_successurl(self):
        createview = EconsensusActionitemCreateView()
        createview.object = ActionItem(id=1)
        createview.kwargs = {'pk': 1}
        assert createview.get_success_url() == reverse('actionitem_detail', kwargs={'decisionpk': 1, 'pk': 1})

    def test_update_get_successurl(self):
        updateview = EconsensusActionitemUpdateView()
        updateview.object = ActionItem(id=1)
        updateview.kwargs = {'decisionpk': 1}
        assert updateview.get_success_url() == reverse('actionitem_detail', kwargs={'decisionpk': 1, 'pk': 1})

    def test_create_get_origin(self):
        # Have get_origin get the pk from url
        createview = EconsensusActionitemCreateView()
        createview.kwargs = {'pk': 1}
        origin = createview.get_origin(RequestFactory())
        assert origin == 1

    def test_create_url(self):
        resolved = resolve(reverse('actionitem_create', kwargs={'pk': 1}))
        assert resolved.func.func_name == 'EconsensusActionitemCreateView'

    def test_update_url(self):
        resolved = resolve(reverse('actionitem_update', kwargs={'decisionpk': 1, 'pk': 1}))
        assert resolved.func.func_name == 'EconsensusActionitemUpdateView'

    def test_list_url(self):
        resolved = resolve(reverse('actionitem_list', kwargs={'org_slug': 'dummy'}))
        assert resolved.func.func_name == 'EconsensusActionitemListView'

    def test_create_login_and_editor_not_logged_in(self):
        get_request = RequestFactory().get('/')
        user = User.objects.create()
        user.is_authenticated = lambda: False
        get_request.user = user
        response = EconsensusActionitemCreateView.as_view()(get_request, pk=1)
        assert response.status_code == 302  # Redirects to login
        user.delete()

    def test_update_login_and_editor_not_logged_in(self):
        get_request = RequestFactory().get('/')
        user = User.objects.create()
        user.is_authenticated = lambda: False
        get_request.user = user
        response = EconsensusActionitemUpdateView.as_view()(get_request)
        assert response.status_code == 302  # Redirects to login
        user.delete()

    def test_list_login_not_logged_in(self):
        get_request = RequestFactory().get('/')
        user = User.objects.create()
        user.is_authenticated = lambda: False
        get_request.user = user
        response = EconsensusActionitemListView.as_view()(get_request)
        assert response.status_code == 302  # Redirects to login
        user.delete()

    def test_list_sort_options_contain_done(self):
        assert 'done' in EconsensusActionitemListView.sort_options

    def test_list_sort_options_doesnt_contain_is_done(self):
        assert not 'is_done' in EconsensusActionitemListView.sort_options

    def test_sort_table_headers_contains_done(self):
        assert 'done' in EconsensusActionitemListView.sort_table_headers['actionitems']

    def test_sort_table_headers_doesnt_contain_is_done(self):
        assert not 'is_done' in EconsensusActionitemListView.sort_table_headers['actionitems']

# Untested:
# templates
# - base (actionitems list)
# - decision_list (actionitems list additions)
# - item_detail
# - actionitem_update (snippet & page)
# - actionitem_detail (snippet)
# javascript
# - item_detail
# - minimizer
# sorting <- will be handled by refactor


class ActionitemsViewTest(DecisionTestCase):

    def setUp(self):
        # ensure the waffle stuff is set up
        Switch.objects.create(name='actionitems', active=True)
        super(ActionitemsViewTest, self).setUp()

    def tearDown(self):
        Switch.objects.all().delete()
        super(ActionitemsViewTest, self).tearDown()

    def test_create_login_and_editor(self):
        decision = self.create_and_return_decision()
        get_request = RequestFactory().get('/')
        get_request.user = self.betty
        # The pk is what django-guardian checks for
        response = EconsensusActionitemCreateView.as_view()(get_request, pk=decision.pk)
        assert response.status_code == 200
        decision.delete()

    def test_create_login_and_editor_noeditor_perms(self):
        decision = self.create_and_return_decision()
        get_request = RequestFactory().get('/')
        assert self.charlie.is_authenticated()  # Confirm user is logged in
        get_request.user = self.charlie
        # The pk is what django-guardian checks for
        response = EconsensusActionitemCreateView.as_view()(get_request, pk=decision.pk)
        assert response.status_code == 403
        decision.delete()

    def test_create_render_and_confirm_origin_and_other_required_fields(self):
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
        decision.delete()

    def test_update_login_and_editor(self):
        decision = self.create_and_return_decision()
        actionitem = ActionItem.objects.create()
        get_request = RequestFactory().get('/')
        get_request.user = self.betty
        response = EconsensusActionitemUpdateView.as_view()(
            get_request, decisionpk=decision.pk, pk=actionitem.pk
        )  # The decisionpk is what django-guardian checks for
        assert response.status_code == 200
        decision.delete()
        actionitem.delete()

    def test_update_login_and_editor_noeditor_perms(self):
        decision = self.create_and_return_decision()
        actionitem = ActionItem.objects.create()
        get_request = RequestFactory().get('/')
        assert self.charlie.is_authenticated()  # Confirm user is logged in
        get_request.user = self.charlie
        response = EconsensusActionitemUpdateView.as_view()(
            get_request, decisionpk=decision.pk, pk=actionitem.pk
        )  # The decisionpk is what django-guardian checks for
        assert response.status_code == 403
        decision.delete()
        actionitem.delete()

    def test_list_login(self):
        get_request = RequestFactory().get('/')
        get_request.user = self.betty
        get_request.session = {}
        response = EconsensusActionitemListView.as_view()(get_request, org_slug=self.bettysorg.slug)
        assert response.status_code == 200

    def test_list_wrongorg(self):
        get_request = RequestFactory().get('/')
        get_request.user = self.betty
        get_request.session = {}
        response = EconsensusActionitemListView.as_view()(get_request, org_slug='wild-about-town')
        assert response.status_code == 200  # This seems like we could aim for better?
        response.render()
        soup = BeautifulSoup(str(response.content))
        assert soup.find("p", {"class": "wrongorg"})

    def test_sends_notification_on_creation(self):
        decision = self.create_and_return_decision()
        notifications.observe(decision, self.betty, ACTIONITEM_NEW)

        mail.outbox = []

        post_request = RequestFactory().post(
            '/',
            {
                'description': u'Lorum Ipsum',
                'responsible': u'Betty',
                'origin': unicode(decision.pk),
                'manager': u'internal'
            }
        )
        post_request.user = self.betty

        EconsensusActionitemCreateView.as_view()(post_request, pk=decision.pk)

        assert len(mail.outbox) > 0, "An email should have been sent to Betty"
        assert mail.outbox[0].subject == "[EC#{0}] An action item was added.".format(decision.pk), mail.outbox[0].subject

        decision.delete()

    def test_sends_notification_on_update(self):
        decision = self.create_and_return_decision()
        actionitem = ActionItem.objects.create(origin=decision)

        mail.outbox = []

        notifications.observe(decision, self.betty, ACTIONITEM_CHANGE)

        post_request = RequestFactory().post(
            '/',
            {
                'actionitem-{0}-description'.format(actionitem.pk): u'Lorum Ipsum',
                'actionitem-{0}-responsible'.format(actionitem.pk): u'Betty',
                'actionitem-{0}-manager'.format(actionitem.pk): u'internal'
            }
        )

        assert self.betty.is_authenticated()  # Confirm user is logged in
        post_request.user = self.betty
        response = EconsensusActionitemUpdateView.as_view()(
            post_request, decisionpk=decision.pk, pk=actionitem.pk
        )  # The decisionpk is what django-guardian checks for

        assert len(mail.outbox) > 0
        assert mail.outbox[0].subject == '[EC#{0}] Action Item {1} was changed.'.format(decision.id, actionitem.id), mail.outbox[0].subject

        decision.delete()
        actionitem.delete()
