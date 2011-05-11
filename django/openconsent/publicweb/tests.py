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
from openconsent.publicweb.forms import DecisionForm

import tinymce.widgets

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
        self.assertEqual(list(Decision.objects.all()),
            list(response.context['decisions']))
    
    def test_decision_add_page(self):
        """
        Test error conditions for the add decision page. 
        """
        path = reverse(openconsent.publicweb.views.decision_add_page)
    
        # Test that the decision add view returns an empty form
        response = self.client.get(path)
        form = DecisionForm()
        self.assertEqual(form.as_p(),
            response.context['decision_form'].as_p())
    
        # Test that the decision add view validates and rejects and empty post
        response = self.client.post(path, dict())
        self.assertFalse(form.is_valid())   # validates the form and adds error messages
        self.assertEqual(form.as_p(),
            response.context['decision_form'].as_p())
        
        # Test that providing a short name is enough to complete the form,
        # save the object and send us back to the home page
        response = self.client.post(path, {'short_name': 'Feed the dog'},
            follow=True)
        self.assertRedirects(response,
            reverse(openconsent.publicweb.views.home_page),
            msg_prefix=response.content)
        
    def test_decision_form_description_field_uses_tinymce_widget(self):
        form = DecisionForm()
        
        self.assertEquals(tinymce.widgets.TinyMCE,
            type(form.fields['description'].widget))
    
        mce_attrs = form._meta.widgets['description'].mce_attrs
        # check the MCE widget is set to advanced theme with our prefered buttons
        self.assertEquals({'theme': 'advanced',
            'theme_advanced_buttons1': 'bold,italic,underline,link,unlink,' + 
                'bullist,blockquote,undo',
            'theme_advanced_buttons3': '',
            'theme_advanced_buttons2': ''}, mce_attrs)
        