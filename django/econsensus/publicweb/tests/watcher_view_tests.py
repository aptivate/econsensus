from django.test.testcases import SimpleTestCase
from django_dynamic_fixture import N
from publicweb.models import Decision
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from publicweb.views import AddWatcherView
from mock import patch, MagicMock

class WatcherViewTests(SimpleTestCase):
    
    @patch('publicweb.views.notification')
    def test_watcher_add_view_adds_observer_to_item(self, notifications):
        decision = N(Decision)
        user = N(User)
        
        mock_view = MagicMock(spec=AddWatcherView)
        mock_view.get_object = lambda: decision
        mock_view.get_user = lambda: user
        mock_view.get = AddWatcherView.get
        
        mock_view.get(mock_view, None)
        notifications.observe.assert_called_with(decision, user, 
          'decision_change')
    
    @patch("publicweb.views.Decision.objects")
    def test_get_object_tries_to_get_decision(self, decisions):
        view = AddWatcherView()
        view.args = []
        view.kwargs = {'decision_id': 1}
        view.get_object()
        decisions.get.assert_called_with(pk=1)
        
    def test_get_user_looks_for_user_in_request(self):
        user = N(User)
        request = RequestFactory().get('')
        request.user = user
        view = AddWatcherView()
        view.request = request
        
        self.assertEqual(user, view.get_user())
        
