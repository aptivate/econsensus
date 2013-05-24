from django.test.client import RequestFactory
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.fields import FieldDoesNotExist
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import AdminSite
from django.contrib.comments import Comment
from django.contrib.sites.models import Site
from django.utils import timezone

from mechanize import ParseString
from organizations.models import Organization
from guardian.shortcuts import assign

from publicweb.models import Decision, Feedback
from publicweb.tests.econsensus_testcase import EconsensusTestCase

class EconsensusFixtureTestCase(EconsensusTestCase):
    fixtures = ['organizations.json', 'users.json']

    def setUp(self):
        self.betty = User.objects.get(username="betty")
        self.charlie = User.objects.get(username="charlie")
        self.bettysorg = Organization.objects.get_for_user(self.betty)[0]
        assign('edit_decisions_feedback', self.betty, self.bettysorg)
        
        self.factory = RequestFactory()
        self.login('betty')

    def login(self, user):
        user = User.objects.get(username=user)
        self.client.login(username=user, password=user)
        self.user = User.objects.get(username=user) 
        return self.user

    def get_form_values_from_response(self, response, number):
        forms = ParseString(response.content, '')
        
        form_data = {}
        for control in forms[number].controls:
            name = control.name
            form_data[name] = control.value
        
        return form_data

    def make_decision(self, **kwargs):
        required = {'description': 'Default description text',
                    'organization': Organization.active.get_for_user(self.user).latest('id'),
                    'status': Decision.PROPOSAL_STATUS}    
        for (key,value) in required.items():
            if key not in kwargs.keys():
                kwargs[key] = value
        return self.make_model_instance(Decision, **kwargs)

    def make_feedback(self, **kwargs):
        required = {'description': 'Default description text',
                    'resolved': False,
                    'author': self.user,
                    'rating': Feedback.DANGER_STATUS}    
        for (key,value) in required.items():
            if key not in kwargs.keys():
                kwargs[key] = value
        return self.make_model_instance(Feedback, **kwargs)
        
    def make_comment(self, **kwargs):
        required = {'comment': 'Default comment text',
                    'user': self.user,
                    'submit_date': timezone.now(),
                    'site':Site.objects.get_current()}
        for (key,value) in required.items():
            if key not in kwargs.keys():
                kwargs[key] = value
        return self.make_model_instance(Comment, **kwargs)
        
    def make_model_instance(self, model, **kwargs):
        instance = model()
        for (key,value) in kwargs.items():
            try:
                instance._meta.get_field(key)
                setattr(instance,key,value)
            except FieldDoesNotExist:
                pass
        instance.full_clean()
        instance.save()
        return instance
                  
    def create_decision_through_browser(self):
        description = 'Quisque sapien justo'
        path = reverse('publicweb_decision_create', args=[self.bettysorg.slug, Decision.DECISION_STATUS])
        post_dict = {'description': description, 
                     'status': Decision.PROPOSAL_STATUS,
                     'watch': True}
        self.client.post(path, post_dict)
        return Decision.objects.get(description=description)
    
    def update_decision_through_browser(self, idd, 
            description = 'Aenean eros nibh'):
        path = reverse('publicweb_decision_update', args=[idd])
        post_dict = {'description': description, 
                     'status': Decision.PROPOSAL_STATUS,
                     'watch': True}
        response = self.client.post(path, post_dict)
        return Decision.objects.get(description=description)
    
    def create_feedback_through_browser(self, idd):
        description = 'a pulvinar tortor bibendum nec'
        path = reverse('publicweb_feedback_create', args=[idd])
        post_dict = {'description': description, 
                     'rating': Feedback.COMMENT_STATUS }
        self.client.post(path, post_dict)
        return Feedback.objects.get(description=description)
    
    def update_feedback_through_browser(self, idd, 
            description = 'nibh ut dignissim. Sed a aliquet quam'):
        path = reverse('publicweb_feedback_update', args=[idd])
        post_dict = {'description': description, 
                     'rating': Feedback.COMMENT_STATUS }
        self.client.post(path, post_dict)
        return Feedback.objects.get(description=description)


    def change_organization_via_admin_screens(self, decision, new_organization=None):
        orig_user = self.user

        admin_user = User.objects.filter(is_staff=True, is_superuser=True)[0]
        self.login(admin_user.username)

        self.change_decision_via_admin(decision, new_organization)

        self.login(orig_user)
        return admin_user

