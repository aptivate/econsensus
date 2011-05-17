#-*- coding: utf-8 -*-

"""
Tests for the public website part of the OpenConsent project
"""
from django.test import TestCase
from django.core.urlresolvers import reverse

from openconsent.publicweb.models import Group

class GroupsTest(TestCase):
    def test_get_list_of_groups(self):
        """
        Test the list of all decision groups is included in the page context.
        """
        response = self.client.get(reverse('groups'))
        self.assertEqual(list(Group.objects.all()),
        list(response.context['groups']))
        
    def test_get_add_decision_list_page_returns_empty_form(self):
        pass
    