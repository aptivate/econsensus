#-*- coding: utf-8 -*-

"""
Tests for the public website part of the OpenConsent project
"""

from __future__ import absolute_import

import logging
import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory

import openconsent.publicweb
import openconsent.publicweb.views
from openconsent.publicweb.models import Decision, Concern
from openconsent.publicweb.forms import DecisionForm, ConcernFormSet

import tinymce.widgets
import django_tables

from operator import attrgetter

import difflib

from mechanize import ParseString

from publicweb.widgets import JQueryUIDateWidget

class DecisionsTest(TestCase):
    def setUp(self):
        pass
        #self.decision = self.get_example_decision()

    def get(self, view_function, **view_args):
        return self.client.get(reverse(view_function, kwargs=view_args))
            
    def test_decision_add_page(self):
        """
        Test error conditions for the add decision page. 
        """
        path = reverse('decision_add')
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
        
        response = self.client.post(path, {'short_name': 'Feed the dog',
                                           'concern_set-TOTAL_FORMS': '3',
                                           'concern_set-INITIAL_FORMS': '0',
                                           'concern_set-MAX_NUM_FORMS': ''},
                                    follow=True)
        
        
        self.assertRedirects(response,
            reverse('decision_list'),
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
    
    def test_decision_form_description_field_uses_tinymce_widget(self):
        self.assert_decision_form_field_uses_tinymce_widget('description')
    
    def test_decisions_table_is_an_instance_of_model_table(self):
        """
        The decisions table is represented using django_tables.ModelTable.
        """
        decision = self.get_example_decision()
        response = self.client.get(reverse('decision_list'))
        decisions_table = response.context['decisions']
        self.assertTrue(isinstance(decisions_table, django_tables.ModelTable))
    
    def assert_decisions_table_sorted_by_date_column(self, column):
        #test fails due to row mismatch...
        # Create test decisions in reverse date order.         
        for i in range(5, 0, -1):
            decision = Decision(short_name='Decision %d' % i)
            setattr(decision, column, datetime.date(2001, 3, i))
            decision.save()
            
        response = self.client.get(reverse('decision_list'),
            data=dict(sort=column))
        decisions_table = response.context['decisions']    
        
        #print getattr(list(decisions_table.rows)[0].data,column)
        
        # Check that decision rows are returned in normal order
        rows = list(decisions_table.rows)

        #print "***Rows data:"
        #for i in range(1, 6):
        #    print "i: ", i, " data: ", getattr(rows[i-1].data, column)

        for i in range(1, 6):
            self.assertEquals(datetime.date(2001, 3, i), getattr(rows[i-1].data, column))
            
    
    def test_decisions_table_rows_can_be_sorted_by_review_date(self):
        self.assert_decisions_table_sorted_by_date_column('review_date')
        
    def test_descisions_table_rows_can_be_sorted_by_decided_date(self):
        self.assert_decisions_table_sorted_by_date_column('decided_date')

    def test_descisions_table_rows_can_be_sorted_by_expiry_date(self):
        self.assert_decisions_table_sorted_by_date_column('expiry_date')

    def get_example_decision(self):
        
        decision = Decision(short_name='Decision Time' )
        decision.save()
        
        concern = Concern(short_name='No time to decide',
                          decision=decision)
        concern.save()
        
        return decision

    def get_diff(self, s1, s2):
        diff = difflib.context_diff(s1, s2)
        str = ''
        for line in diff:
            str += line
            
        return str
        
    def test_view_edit_decision_page(self):
        decision = self.get_example_decision()
        
        path = reverse(openconsent.publicweb.views.decision_view_page, 
                       args=[decision.id])
        response = self.client.get(path)
        
        test_form_str = str(DecisionForm(instance=decision))
        decision_form_str = str(response.context['decision_form'])
        
        self.assertEqual(test_form_str, decision_form_str,
                         self.get_diff(test_form_str, decision_form_str))

    def test_edit_decision_page_has_concern_formset(self):
        decision = self.get_example_decision()
        
        path = reverse('decision_edit', args=[decision.id])
        response = self.client.get(path)
        
        concern_formset = response.context['concern_form']
        concerns = decision.concern_set.all()
        self.assertEquals(list(concerns), list(concern_formset.queryset))

    def get_edit_concern_response(self, decision):
        path = reverse(openconsent.publicweb.views.decision_view_page,
                       args=[decision.id])
        response = self.client.post(path, {'short_name': 'Modified',
                                    'concern_set-TOTAL_FORMS': '3',
                                    'concern_set-INITIAL_FORMS': '0',
                                    'concern_set-MAX_NUM_FORMS': '',
                                    'concern_set-1-short_name': 'This concern is modified',
                                    'concern_set-2-short_name': 'No one wants them',
                                    })
        return response
    

        
    def test_edit_decision_page_update_concern(self):
        self.decision = self.get_example_decision()
        
        #concern_formset = ConcernFormSet(instance=self.decision)
        path = reverse('decision_edit', args=[self.decision.id])
        
        page = self.client.get(path)
        
        post_data = self.mechanize_page(page.content)
               
        post_data['concern_set-0-short_name'] = 'Modified'
                
        #post_data.update(concern_formset.management_form.initial)
                
        self.client.post(path, post_data)
        
        decision = Decision.objects.get(id=self.decision.id)
                
        self.assertEquals('Modified', decision.concern_set.all()[0].short_name)
        
    def get_edit_decision_response(self, decision):
        path = reverse(openconsent.publicweb.views.decision_view_page,
                       args=[decision.id])
        response = self.client.post(path, {'short_name': 'Feed the cat',
                                           'concern_set-TOTAL_FORMS': '3',
                                           'concern_set-INITIAL_FORMS': '0',
                                           'concern_set-MAX_NUM_FORMS': '',
                                           })
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
        self.assertRedirects(response, reverse('decision_list'),
            msg_prefix=response.content)
        
   
    def test_decision_add_page_has_concerns_form(self):
        response = self.client.get(reverse('decision_add'))        
        self.assertTrue('concern_form' in response.context, 
                        "\"concern_form\" not in this context")
    
    def test_add_decision_with_concerns(self):
        response = self.client.post(reverse('decision_add'), 
                                    {'short_name': 'Make Eggs',
                                    'concern_set-TOTAL_FORMS': '3',
                                    'concern_set-INITIAL_FORMS': '0',
                                    'concern_set-MAX_NUM_FORMS': '',
                                    'concern_set-0-short_name': 'The eggs are bad',
                                    'concern_set-1-short_name': 'No one wants them',
                                    })

        decision = Decision.objects.all()[0]
                
        concerns = decision.concern_set.all()
        
        self.assertEquals('The eggs are bad', concerns[0].short_name)
        self.assertEquals('No one wants them', concerns[1].short_name)
    
    def assert_decision_datepickers(self,field):
        form = DecisionForm()
        
        self.assertEquals(JQueryUIDateWidget,
            type(form.fields[field].widget))
        
    def test_decided_datepickers(self):
        self.assert_decision_datepickers('decided_date')

    def test_effective_datepickers(self):
        self.assert_decision_datepickers('effective_date')

    def test_review_datepickers(self):
        self.assert_decision_datepickers('review_date')

    def test_expiry_datepickers(self):
        self.assert_decision_datepickers('expiry_date')
    
    #TODO: Needs to work for select elements
    def mechanize_page(self,content):
        forms = ParseString(content, '')
        
        length = len(forms[1].controls)
        form_data = {}
        for control in range(length):
            try:
                 name = forms[1].controls[control].attrs.get("name")
                 if name:
                     if forms[1].controls[control].attrs.get("value") != None:
                         form_data[name]=forms[1].controls[control].attrs.get("value")
                     else:
                         form_data[name]=''

            except AttributeError:
                pass
        
        return form_data
                    
 #   def test_mechanize_page(self):
 #       #Basic test to see if the mechanize package works.
 #       path = reverse('decision_edit', args=[self.decision.id])
 #       form_data = self.mechanize_page(path)
        
            