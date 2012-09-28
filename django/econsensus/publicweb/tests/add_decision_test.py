from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from organizations.models import Organization
from publicweb.models import Decision
from publicweb.views import DecisionCreate
from decision_test_case import DecisionTestCase

class AddDecisionTest(DecisionTestCase):
    fixtures = ['organizations.json', 'users.json']

    def setUp(self):
        self.betty = User.objects.get(username="betty")
        self.bettysorg = Organization.objects.get_for_user(self.betty)[0]
        self.factory = RequestFactory()
    
    def test_jquery_javascript_included_in_page(self):
        response = self.load_add_decision_and_return_response()
        
        self.assertContains(response, "jquery.min.js")
        self.assertContains(response, "jquery-ui.min.js")
        
    def test_jquery_css_included_in_page(self):
        response = self.load_add_decision_and_return_response()
        self.assertContains(response, "jquery-ui.css")

    def test_add_description_form_doesnt_ask_for_name(self):
        response = self.load_add_decision_and_return_response()
        self.assertNotContains(response, "id_short_name")
    
    def load_add_decision_and_return_response(self):
        request = self.factory.request()
        request.user = self.betty
        kwargs = {'org_slug':self.bettysorg.slug}
        response = DecisionCreate(template_name='decision_update_page.html').dispatch(request, **kwargs)
        rendered_response = response.render()
        return rendered_response
