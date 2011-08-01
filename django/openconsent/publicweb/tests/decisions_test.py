#-*- coding: utf-8 -*-

"""
Tests for the public website part of the OpenConsent project
"""

from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from publicweb.views import edit_decision
from publicweb.models import Decision
from publicweb.forms import DecisionForm

import tinymce.widgets

import difflib

from publicweb.widgets import JQueryUIDateWidget
from publicweb.tests.decision_test_case import DecisionTestCase

class DecisionsTest(DecisionTestCase):
    def get(self, view_function, **view_args):
        return self.client.get(reverse(view_function, kwargs=view_args))
            
    def test_add_decision(self):
        """
        Test error conditions for the add decision page. 
        """
        path = reverse('add_decision')
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
        
        post_dict = self.get_default_decision_form_dict()
        
        post_dict.update({'short_name': 'Feed the dog',
                       'feedback_set-TOTAL_FORMS': '3',
                       'feedback_set-INITIAL_FORMS': '0',
                       'feedback_set-MAX_NUM_FORMS': ''})
        
        response = self.client.post(path, post_dict,
                                    follow=True)
        
        
        self.assertRedirects(response,
            reverse('decision_list'),
            msg_prefix=response.content)

    def get_default_decision_form_dict(self):
        return {'status': 1}

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

    def get_diff(self, s1, s2):
        diff = difflib.context_diff(s1, s2)
        str = ''
        for line in diff:
            str += line
            
        return str
        
    def test_edit_decision(self):
        decision = self.create_and_return_example_decision_with_feedback()
        
        path = reverse(edit_decision, 
                       args=[decision.id])
        response = self.client.get(path)
        
        test_form_str = str(DecisionForm(instance=decision))
        decision_form_str = str(response.context['decision_form'])
        
        self.assertEqual(test_form_str, decision_form_str,
                         self.get_diff(test_form_str, decision_form_str))

    def test_edit_decision_has_feedback_formset(self):
        decision = self.create_and_return_example_decision_with_feedback()
        
        path = reverse('edit_decision', args=[decision.id])
        response = self.client.get(path)
        
        feedback_formset = response.context['feedback_formset']
        feedback = decision.feedback_set.all()
        self.assertEquals(list(feedback), list(feedback_formset.queryset))

    def get_edit_feedback_response(self, decision):
        path = reverse(edit_decision,
                       args=[decision.id])
        response = self.client.post(path, {'short_name': 'Modified',
                                    'feedback_set-TOTAL_FORMS': '3',
                                    'feedback_set-INITIAL_FORMS': '0',
                                    'feedback_set-MAX_NUM_FORMS': '',
                                    'feedback_set-1-short_name': 'This feedback has been modified',
                                    'feedback_set-2-short_name': 'No one wants them',
                                    })
        return response
    
    def test_edit_decision_update_feedback(self):
        self.decision = self.create_and_return_example_decision_with_feedback()
        
        path = reverse('edit_decision', args=[self.decision.id])
        page = self.client.get(path)
        
        post_data = self.get_form_values_from_response(page)
        post_data['feedback_set-0-short_name'] = 'Modified'
        self.client.post(path, post_data)
        
        decision = Decision.objects.get(id=self.decision.id)
        self.assertEquals('Modified', decision.feedback_set.all()[0].short_name)
        
    def get_edit_decision_response(self, decision):
        path = reverse(edit_decision,
                       args=[decision.id])
        post_dict = self.get_default_decision_form_dict()
        post_dict.update({'short_name': 'Feed the cat',
                           'feedback_set-TOTAL_FORMS': '3',
                           'feedback_set-INITIAL_FORMS': '0',
                           'feedback_set-MAX_NUM_FORMS': '',
                           })
        response = self.client.post(path, post_dict)
        return response
    
    def test_save_edit_decision(self):
        decision = self.create_and_return_example_decision_with_feedback()
        # we are only interested in the side effect of saving a decision
        self.get_edit_decision_response(decision)
        
        decision_db = Decision.objects.get(id=decision.id)
        self.assertEquals('Feed the cat', decision_db.short_name)
    
    def test_redirect_after_edit_decision(self):       
        decision = self.create_and_return_example_decision_with_feedback()
        response = self.get_edit_decision_response(decision)
        self.assertRedirects(response, reverse('decision_list'),
            msg_prefix=response.content)
        
   
    def test_add_decision_has_feedback_form(self):
        response = self.client.get(reverse('add_decision'))        
        self.assertTrue('feedback_formset' in response.context, 
                        "\"feedback_formset\" not in this context")
    
    def test_add_decision_with_feedback(self):
        post_dict = self.get_default_decision_form_dict()
        post_dict.update({'short_name': 'Make Eggs',
                            'feedback_set-TOTAL_FORMS': '3',
                            'feedback_set-INITIAL_FORMS': '0',
                            'feedback_set-MAX_NUM_FORMS': '',
                            'feedback_set-0-short_name': 'The eggs are bad',
                            'feedback_set-1-short_name': 'No one wants them'})
        
        response = self.client.post(reverse('add_decision'), 
                                post_dict,
                                follow=True )
        self.assertEqual(1, len(Decision.objects.all()), "Failed to create object" + response.content)
        decision = Decision.objects.all()[0]
               
        feedback = decision.feedback_set.all()
        
        self.assertEquals('The eggs are bad', feedback[0].short_name)
        self.assertEquals('No one wants them', feedback[1].short_name)
    
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
        
    def test_decision_has_status(self):
        decision = self.create_and_return_example_decision_with_feedback()
        self.assertEquals(0, getattr(decision, "status"), 
                          "Decision does not have a status")
        
    def test_decision_has_watchers(self):
        decision = self.create_and_return_decision()
        self.assertEquals(True, hasattr(decision, "watchers"), 
                          "Decision does not have a 'watchers' attribute")
        
    def test_decision_watchers_is_updated(self):
        decision = self.create_and_return_decision()
        watchers = getattr(decision, "watchers")
                
        self.assertTrue(self.user in watchers.all(), 
                          "Decision watchers not updated")
        

