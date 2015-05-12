from StringIO import StringIO
import sys

from django.core import management

from waffle import Switch, Flag, Sample

from publicweb.tests.open_consent_test_case import EconsensusFixtureTestCase


class WaffleCommandTest(EconsensusFixtureTestCase):

    fixtures = ['default_waffles.json']

    def setUp(self):
        self.output = StringIO()
        self.saved_output = sys.stdout
        sys.stdout = self.output

    def tearDown(self):
        self.output.close()
        sys.stdout = self.saved_output

    def _delete_waffles(self):
        """Delete all waffles"""
        for switch in Switch.objects.all():
            switch.delete()
        for flag in Flag.objects.all():
            flag.delete()
        for sample in Sample.objects.all():
            sample.delete()

    def _requires_initializing(self):
        """Returns true if waffles need initializing, False if not."""
        management.call_command('waffles_need_initializing')
        output = self.output.getvalue()
        return int(output.strip()) == 1

    def test_having_no_waffles_requires_initializing(self):
        self._delete_waffles()
        self.assertTrue(self._requires_initializing())

    def test_if_switch_is_present_no_initialization_is_required(self):
        self._delete_waffles()
        switch = Switch(name='test')
        switch.save()
        self.assertFalse(self._requires_initializing())

    def test_if_flag_is_present_no_initialization_is_required(self):
        self._delete_waffles()
        flag = Flag(name='test')
        flag.save()
        self.assertFalse(self._requires_initializing())

    def test_if_sample_is_present_no_initialization_is_required(self):
        self._delete_waffles()
        sample = Sample(name='test', percent=0)
        sample.save()
        self.assertFalse(self._requires_initializing())
