from django.test.testcases import SimpleTestCase
from django_dynamic_fixture import N
from publicweb.models import Decision
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from publicweb.views import AddWatcher, RemoveWatcher
from mock import patch, MagicMock

class WatcherViewTests(SimpleTestCase):
    
    def test_add_watcher_view_adds_observer_to_item(self):
        decision = N(Decision)
        user = N(User)
        
        mock_view = MagicMock(spec=AddWatcher)
        mock_view.get_object = lambda: decision
        mock_view.get_user = lambda: user
        mock_view.get = AddWatcher.get
        
        mock_view.get(mock_view, RequestFactory().get('/', {'next': '/'}))
        mock_view.observation_method.assert_called_with(decision, user, 
          'decision_change')
    
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

    def test_remove_watcher_view_removes_observer_from_item(self):
        decision = N(Decision)
        user = N(User)
        
        mock_view = MagicMock(spec=RemoveWatcher)
        mock_view.get_object = lambda: decision
        mock_view.get_user = lambda: user
        mock_view.get = RemoveWatcher.get

        mock_view.get(mock_view, RequestFactory().get('/', {'next': '/'}))
        mock_view.observation_method.assert_called_with(decision, user, 
          'decision_change')