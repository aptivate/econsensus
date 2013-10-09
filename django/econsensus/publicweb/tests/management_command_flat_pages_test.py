import sys
from StringIO import StringIO
from unittest import TestCase

from django.contrib.flatpages.models import FlatPage
from django.core import management


class CommandFlatPageNeedsInitializingTests(TestCase):

    def setUp(self):
        self.assertEqual(FlatPage.objects.count(), 0)
        self.output = StringIO()
        self.saved_output = sys.stdout
        sys.stdout = self.output

    def tearDown(self):
        self.output.close()
        sys.stdout = self.saved_output
        FlatPage.objects.all().delete()

    def create_page(self, name):
        url = '/' + name + '/'
        FlatPage.objects.create(url=url, title=name, content=name,
                                enable_comments=False,
                                registration_required=False)

    def test_returns_1_when_no_pages_exist(self):
        management.call_command('flatpages_needs_initializing')
        output = self.output.getvalue()
        self.assertEqual("1", output.strip())

    def test_returns_0_when_both_pages_exist(self):
        self.create_page('help')
        self.create_page('about')
        management.call_command('flatpages_needs_initializing')
        output = self.output.getvalue()
        self.assertEqual("0", output.strip())

    def test_returns_1_when_only_help_page_exists(self):
        self.create_page('help')
        management.call_command('flatpages_needs_initializing')
        output = self.output.getvalue()
        self.assertEqual("1", output.strip())

    def test_returns_1_when_only_about_page_exists(self):
        self.create_page('about')
        management.call_command('flatpages_needs_initializing')
        output = self.output.getvalue()
        self.assertEqual("1", output.strip())

    def test_returns_1_when_two_other_pages_exist(self):
        self.create_page('other')
        self.create_page('content')
        management.call_command('flatpages_needs_initializing')
        output = self.output.getvalue()
        self.assertEqual("1", output.strip())
