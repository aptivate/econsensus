#-*- coding: utf-8 -*-

"""
Tests for the public website part of the OpenConsent project
"""

from __future__ import absolute_import

import logging

from django.test import TestCase
from django.core.urlresolvers import reverse

import openconsent.publicweb
import openconsent.publicweb.views
from openconsent.publicweb.models import Decision

class PublicWebsiteTest(TestCase):
    # fixtures = ['submission_test_data.json', 'foobar', 'indicator_tests.yaml']
    
    def setUp(self):
        # self.foobar = Agency.objects.get(agency="Foobar")
        # self.mozambique = Country.objects.get(country="Mozambique")
        pass

    def get(self, view_function, **view_args):
        return self.client.get(reverse(view_function, kwargs=view_args))
    
    def test_get_homepage(self):
        response = self.get(openconsent.publicweb.views.home_page)
        self.assertEqual(list(Decision.objects.all()), response.context['decisions'])