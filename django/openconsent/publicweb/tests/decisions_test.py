#-*- coding: utf-8 -*-

"""
Tests for the public website part of the OpenConsent project
"""

from __future__ import absolute_import

import logging
import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse

import openconsent.publicweb
import openconsent.publicweb.views
from openconsent.publicweb.models import Decision, Group
from openconsent.publicweb.forms import DecisionForm

import tinymce.widgets
import django_tables

from operator import attrgetter

import difflib

class DecisionsTest(TestCase):
    # fixtures = ['submission_test_data.json', 'foobar', 'indicator_tests.yaml']
    
    def setUp(self):
        # self.foobar = Agency.objects.get(agency="Foobar")
        # self.mozambique = Country.objects.get(country="Mozambique")
        pass

    def get(self, view_function, **view_args):
        return self.client.get(reverse(view_function, kwargs=view_args))
   

    def test_get_decision_list_page_with_invalid_decisionlist_id_returns_404(self):
        response = self.client.get(reverse('decision_list', args = [100]))
        self.assertTemplateUsed(response, '404.html')
        
    def test_check_decision_title(self):
        """
        Check the decision title matches its parent list
        """
        group = Group(short_name='First List')
        group.save()        
        
        response = self.client.get(reverse('decision_list', args = [group.id]))
        self.assertEqual(group.short_name,
                         response.context['group'].short_name)
    
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
        group = Group(short_name='First List')
        group.save()
        
        response = self.client.post(path, {'short_name': 'Feed the dog',
                                           'group': group.id },
            follow=True)
        
        
        self.assertRedirects(response,
            reverse('decision_list', args=[group.id]),
            msg_prefix=response.content)

    def assert_decision_form_field_uses_tinymce_widget(self, field):
        form = DecisionForm()
        
        self.assertEquals(tinymce.widgets.TinyMCE,
            type(form.fields[field].widget))
    
        mce_attrs = form._meta.widgets[field].mce_attrs
        # check the MCE widget is set to advanced theme with our preferred buttons
        self.assertEquals({'theme': 'advanced',
            'theme_advanced_buttons1': 'bold,italic,underline,link,unlink,' + 
                'bullist,blockquote,undo',
            'theme_advanced_buttons3': '',
            'theme_advanced_buttons2': ''}, mce_attrs)
    
    def test_decision_form_concerns_field_uses_tinymce_widget(self):
        self.assert_decision_form_field_uses_tinymce_widget('concerns')

    def test_decision_form_description_field_uses_tinymce_widget(self):
        self.assert_decision_form_field_uses_tinymce_widget('description')
    
    def test_decisions_table_is_an_instance_of_model_table(self):
        """
        The decisions table is represented using django_tables.ModelTable.
        """
        decision = self.get_example_decision()
        response = self.client.get(reverse('decision_list',
                                    args=[decision.group.id]))
        decisions_table = response.context['decisions']
        self.assertTrue(isinstance(decisions_table, django_tables.ModelTable))
    
    def assert_decisions_table_sorted_by_date_column(self, column):
        # Create test decisions in reverse date order. 
        group = Group(short_name='First List')
        group.save()
        
        for i in range(5, 0, -1):
            decision = Decision(short_name='Decision %d' % i)
            decision.group = group
            setattr(decision, column, datetime.date(2001, 3, i))
            decision.save()
            
        response = self.client.get(reverse('decision_list',
                                           args=[group.id]),
            data=dict(sort=column))
        decisions_table = response.context['decisions']    
        
        # Check that decision rows are returned in normal order
        rows = list(decisions_table.rows)
        for i in range(1, 6):
            self.assertEquals(datetime.date(2001, 3, i), getattr(rows[i-1].data, column))
    
    def test_decisions_table_rows_can_be_sorted_by_review_date(self):
        self.assert_decisions_table_sorted_by_date_column('review_date')
        
    def test_descisions_table_rows_can_be_sorted_by_decided_date(self):
        self.assert_decisions_table_sorted_by_date_column('decided_date')

    def test_descisions_table_rows_can_be_sorted_by_expiry_date(self):
        self.assert_decisions_table_sorted_by_date_column('expiry_date')

    def get_example_decision(self):
        
        group = Group(short_name='First List')
        group.save()
        
        decision = Decision(short_name='Decision Time' )
        decision.group = group
        decision.save()
        
        return decision

    def get_diff(self, s1, s2):
        diff = difflib.context_diff(s1, s2)
        str = ''
        for line in diff:
            str += line
            
        return str
        
    def test_view_edit_decision_page(self):
        decision = self.get_example_decision()
        
        path = reverse(openconsent.publicweb.views.decision_view_page, args=[decision.id])
        response = self.client.get(path)
        
        test_form_str = str(DecisionForm(instance=decision))
        decision_form_str = str(response.context['decision_form'])
        
        self.assertEqual(test_form_str, decision_form_str,
                         self.get_diff(test_form_str, decision_form_str))

    def get_edit_decision_response(self, decision):
        path = reverse(openconsent.publicweb.views.decision_view_page, args=[decision.id])
        response = self.client.post(path, {'short_name': 'Feed the cat',
                                           'group': decision.group.id})
        return response
    
    def test_save_edit_decision_page(self):
        decision = self.get_example_decision()
        # we are only interested in the side effect of saving a decision
        self.get_edit_decision_response(decision)
        
        decision_db = Decision.objects.get(id=decision.id)
        self.assertEquals('Feed the cat', decision_db.short_name)
    
    def test_redirect_after_edit_decision_page(self):       
        decision = self.get_example_decision()
        response = self.get_edit_decision_response(decision)
        self.assertRedirects(response, reverse('decision_list',
                                               args=[decision.group.id]),
            msg_prefix=response.content)
        
    def test_decision_list_only_shows_decisions_from_a_single_group(self):
        breakfast_decisions = Group(short_name='Breakfast decisions')
        breakfast_decisions.save()
        lunch_decisions = Group(short_name='Lunch decisions')
        lunch_decisions.save()
        
        eggs = Decision(short_name='Make Eggs', group=breakfast_decisions)
        eggs.save()
        toast = Decision(short_name='Make Toast', group=breakfast_decisions)
        toast.save()
        Decision(short_name='Make salad', group=lunch_decisions).save()
        
         
        expected_decisions = sorted([eggs,toast],key=attrgetter('id'))
        
        response = self.client.get(reverse('decision_list',
                                            args=[breakfast_decisions.id]))
        
        actual_data = response.context['decisions']
              
        actual_decisions = []
        
        for row in actual_data.rows:
            actual_decisions.append(row.data)
                
        actual_decisions = sorted(actual_decisions,key=attrgetter('id'))
        
        self.assertEqual(expected_decisions, actual_decisions)
    
 