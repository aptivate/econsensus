from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from mechanize import ParseString
from publicweb.models import Decision, Feedback

class OpenConsentTestCase(TestCase):
    password_stump = 'password'
    
    def setUp(self):
        self.adam = User.objects.create_user('Adam', 'adam@econsensus.com', self.password_stump)
        self.barry = User.objects.create_user('Barry', 'barry@econsensus.com', self.password_stump)
        self.charlie = User.objects.create_user('Charlie', 'charlie@econsensus.com', self.password_stump)
        self.user = self.login('Adam')

    def login(self, user):
        self.client.login(username=user, password=self.password_stump)
        self.user = User.objects.get(username=user) 
        return self.user

    def get_form_values_from_response(self, response, number):
        forms = ParseString(response.content, '')
        
        form_data = {}
        for control in forms[number].controls:
            name = control.name
            form_data[name] = control.value
        
        return form_data

    def create_decision_through_browser(self):
        description = 'Quisque sapien justo'
        path = reverse('publicweb_decision_create', args=[Decision.DECISION_STATUS])
        post_dict = {'description': description, 
                     'status': Decision.PROPOSAL_STATUS,
                     'watch': True}
        self.client.post(path, post_dict)
        return Decision.objects.get(description=description)
    
    def update_decision_through_browser(self, idd):
        description = 'Aenean eros nibh'
        path = reverse('publicweb_decision_update', args=[idd])
        post_dict = {'description': description, 
                     'status': Decision.PROPOSAL_STATUS,
                     'watch': True}
        self.client.post(path, post_dict)
        return Decision.objects.get(description=description)
    
    def create_feedback_through_browser(self,idd):
        description = 'a pulvinar tortor bibendum nec'
        path = reverse('publicweb_feedback_create', args=[idd])
        post_dict = {'description': description, 
                     'rating': Feedback.COMMENT_STATUS }
        self.client.post(path,post_dict)
        return Feedback.objects.get(description=description)
    
    def update_feedback_through_browser(self, idd):
        description = 'nibh ut dignissim. Sed a aliquet quam'
        path = reverse('publicweb_feedback_update', args=[idd])
        post_dict = {'description': description, 
                     'rating': Feedback.COMMENT_STATUS }
        self.client.post(path, post_dict)
        return Feedback.objects.get(description=description)
