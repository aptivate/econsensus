from StringIO import StringIO
import sys

from django.conf import settings
from django.contrib.sites.models import Site
from django.core import management

from publicweb.tests.open_consent_test_case import EconsensusFixtureTestCase

class SiteDataCommandTest(EconsensusFixtureTestCase):


    def setUp(self):
        # django.contrib.sites creates a Site with example domain when table is created
        self.assertEqual(Site.objects.get(id=settings.SITE_ID).domain, 'example.com')
        self.assertEqual(Site.objects.exclude(id=settings.SITE_ID).count(), 0)
        self.output = StringIO()
        self.saved_output = sys.stdout
        sys.stdout = self.output

    def tearDown(self):
        self.output.close()
        sys.stdout = self.saved_output
    
    def test_when_no_site_for_our_app(self):
        Site.objects.get(id=settings.SITE_ID).delete()
        management.call_command('site_needs_initializing')
        output = self.output.getvalue()
        self.assertTrue(int(output.strip()))
    
    def test_when_no_site_for_our_app_and_some_others_exist(self):
        Site(domain='domain.com', name='Name').save()
        Site(domain='domain2.com', name='Name2').save()
        Site.objects.get(id=settings.SITE_ID).delete()
        management.call_command('site_needs_initializing')
        output = self.output.getvalue()
        self.assertTrue(int(output.strip()))
    
    def test_when_our_site_is_example(self):
        management.call_command('site_needs_initializing')
        output = self.output.getvalue()
        self.assertTrue(int(output.strip()))
    
    def test_when_our_site_is_example_and_some_others_exist(self):
        Site(domain='domain.com', name='Name').save()
        Site(domain='domain2.com', name='Name2').save()
        management.call_command('site_needs_initializing')
        output = self.output.getvalue()
        self.assertTrue(int(output.strip()))
    
    def test_when_our_site_not_example(self):
        our_site = Site.objects.get(id=settings.SITE_ID)
        our_site.domain = 'importantdomain.com'
        our_site.name = 'important name'
        our_site.save()
        management.call_command('site_needs_initializing')
        output = self.output.getvalue()
        self.assertFalse(int(output.strip()))
    
    def test_when_our_site_not_example_and_some_others_exist(self):
        our_site = Site.objects.get(id=settings.SITE_ID)
        our_site.domain = 'importantdomain.com'
        our_site.name = 'important name'
        our_site.save()
        Site(domain='domain.com', name='Name').save()
        Site(domain='domain2.com', name='Name2').save()
        management.call_command('site_needs_initializing')
        output = self.output.getvalue()
        self.assertFalse(int(output.strip()))
    
