from django.contrib.auth.models import User
from django.test.client import RequestFactory
from django.test.testcases import SimpleTestCase
from django_dynamic_fixture import N
from mock import patch, MagicMock
from signals.management import DECISION_CHANGE

from publicweb.models import Decision
from publicweb.views import AddWatcher, RemoveWatcher


class WatcherViewTests(SimpleTestCase):

    @patch('publicweb.views.notification')
    def test_add_watcher_view_adds_observer_to_item(self, notifications):
        # A watcher is only added if the item isn't already being watched so we
        # explicitly set is_observing to False
        notifications.is_observing = lambda decision, user: False

        decision = N(Decision)
        user = N(User)

        mock_view = MagicMock(spec=AddWatcher)
        mock_view.get_object = lambda: decision
        mock_view.get_user = lambda: user
        mock_view.get = AddWatcher.get

        mock_view.get(mock_view, RequestFactory().get('/', {'next': '/'}))
        notifications.observe.assert_called_with(
            decision, user, DECISION_CHANGE)

    @patch("publicweb.views.Decision.objects")
    def test_get_object_tries_to_get_decision(self, decisions):
        view = AddWatcher()
        view.args = []
        view.kwargs = {'decision_id': 1}
        view.get_object()
        decisions.get.assert_called_with(pk=1)

    def test_get_user_looks_for_user_in_request(self):
        user = N(User)
        request = RequestFactory().get('')
        request.user = user
        view = AddWatcher()
        view.request = request

        self.assertEqual(user, view.get_user())

    @patch('publicweb.views.notification')
    def test_remove_watcher_view_removes_observer_from_item(self, notifications):
        decision = N(Decision)
        user = N(User)

        mock_view = MagicMock(spec=RemoveWatcher)
        mock_view.get_object = lambda: decision
        mock_view.get_user = lambda: user
        mock_view.get = RemoveWatcher.get

        mock_view.get(mock_view, RequestFactory().get('/', {'next': '/'}))
        notifications.stop_observing.assert_called_with(decision, user)
