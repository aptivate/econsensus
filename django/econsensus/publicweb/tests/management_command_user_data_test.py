from StringIO import StringIO
import sys

from django.conf import settings
from django.contrib.auth.models import User
from django.core import management

from publicweb.tests.open_consent_test_case import EconsensusTestCase

class UserDataCommandTest(EconsensusTestCase):

    fixtures = ['default_auth_user.json']
    # django-guardian will have created an AnonymousUser at table creation

    def setUp(self):
        self.output = StringIO()
        self.saved_output = sys.stdout
        sys.stdout = self.output

    def tearDown(self):
        self.output.close()
        sys.stdout = self.saved_output
    
    def test_when_no_users(self):
        for user in User.objects.all():
            user.delete()
        management.call_command('auth_user_needs_initializing')
        output = self.output.getvalue()
        self.assertTrue(int(output.strip()))
    
    def test_when_only_guardian_anon_user(self):
        for user in User.objects.exclude(id=settings.ANONYMOUS_USER_ID):
            user.delete()
        management.call_command('auth_user_needs_initializing')
        output = self.output.getvalue()
        self.assertTrue(int(output.strip()))
    
    def test_when_only_one_live_user(self):
        for user in User.objects.all():
            user.delete()
        User.objects.create_user('liveuser', '', 'password')
        management.call_command('auth_user_needs_initializing')
        output = self.output.getvalue()
        self.assertFalse(int(output.strip()))
    
    def test_when_anon_and_some_live_users(self):
        management.call_command('auth_user_needs_initializing')
        output = self.output.getvalue()
        self.assertFalse(int(output.strip()))
    
    def test_when_some_live_users(self):
        User.objects.get(id=settings.ANONYMOUS_USER_ID).delete()
        management.call_command('auth_user_needs_initializing')
        output = self.output.getvalue()
        self.assertFalse(int(output.strip()))
    
