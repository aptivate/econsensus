#-*- coding: utf-8 -*-

"""
Tests for the public website part of the OpenConsent project
"""
from django.core.urlresolvers import reverse
from django.forms.fields import BooleanField
from django.forms.widgets import CheckboxInput

import difflib

from publicweb.models import Decision
from publicweb.forms import DecisionForm
from publicweb.widgets import JQueryUIDateWidget
from decision_test_case import DecisionTestCase

### As a general note, I can see our tests are evolving into...
### 1 - model tests (does the model have x property?)
### 2 - form tests (does the form have x field?)
### 3 - browser tests (does page respond correct? does submission work OK?)

class DecisionsTest(DecisionTestCase):
    def get(self, view_function, **view_args):
        return self.client.get(reverse(view_function, kwargs=view_args))
            
    def test_add_decision(self):
        """
        Test error conditions for the add decision page. 
        """
        path = reverse('publicweb_decision_create', args=[Decision.PROPOSAL_STATUS])
        # Test that the decision add view returns an empty form
        actual = self.client.get(path).context['form'].as_p().splitlines()
        
        expected = DecisionForm().as_p().splitlines()

        self.assertEqual(expected, actual)
            
        # Test that the decision add view validates and rejects and empty post
        post_dict = self.get_default_decision_form_dict()

        response = self.client.post(path, post_dict)

        self.assertFalse(response.context['form'].is_valid())
        
        # Test that providing a short name is enough to complete the form,
        # save the object and send us back to the home page
        
        post_dict = self.get_default_decision_form_dict()

        post_dict.update({  'description': 'Make Eggs',
                            'watch': False,
                            'submit': "Submit"})        
       
        response = self.client.post(path, post_dict,
                                    follow=True)
        
        
        self.assertRedirects(response,
            reverse('publicweb_item_list', args=['decision']),
            msg_prefix=response.content)

    def get_default_decision_form_dict(self):
        return {'status': Decision.DECISION_STATUS}

    def get_diff(self, s1, s2): #pylint: disable-msg=C0103
        diff = difflib.context_diff(s1, s2)
        rope = ''
        for line in diff:
            rope += line
            
        return rope
        
    def test_decision_form(self):
        decision = self.create_and_return_example_decision_with_feedback()
        
        path = reverse('publicweb_decision_update', 
                       args=[decision.id])
        response = self.client.get(path)
        self.assertTrue(isinstance(response.context['form'], DecisionForm))

    def get_edit_feedback_response(self, decision):
        path = reverse('publicweb_decision_update',
                       args=[decision.id])
        response = self.client.post(path, {'description': 'Modified',
                                    'feedback_set-TOTAL_FORMS': '3',
                                    'feedback_set-INITIAL_FORMS': '0',
                                    'feedback_set-MAX_NUM_FORMS': '',
                                    'feedback_set-1-description': 'This feedback has been modified',
                                    'feedback_set-2-description': 'No one wants them',
                                    })
        return response
    
    def test_update_feedback(self):
        decision = self.create_and_return_example_decision_with_feedback()
        feedback = decision.feedback_set.all()[0]
        
        path = reverse('publicweb_feedback_update', args=[feedback.id])        
        post_data = {'description': 'Modified', 'submit': 'Submit'}
        
        self.client.post(path, post_data)
        
        decision = Decision.objects.get(id=decision.id)
        self.assertEquals('Modified', decision.feedback_set.all()[0].description)
        
    def get_edit_decision_response(self, decision):
        path = reverse('publicweb_decision_update',
                       args=[decision.id])
        post_dict = self.get_default_decision_form_dict()
        post_dict.update({'description': 'Feed the cat',
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
        self.assertEquals('Feed the cat', decision_db.description)
    
    def test_redirect_after_edit_decision(self):       
        decision = self.create_and_return_example_decision_with_feedback()
        response = self.get_edit_decision_response(decision)
        self.assertRedirects(response, reverse('publicweb_item_list', args=['decision']),
            msg_prefix=response.content)
            
    def test_add_feedback(self):
        decision = Decision(status=Decision.PROPOSAL_STATUS, description='Make Eggs')
        decision.save()
        post_dict= {'rating': '2', 'description': 'The eggs are bad'}
        response = self.client.post(reverse('publicweb_feedback_create', args=[decision.id]), 
                                post_dict,
                                follow=True )        
        feedback = decision.feedback_set.all()[:1].get()
        self.assertEquals('The eggs are bad', feedback.description)
    
    def assert_decision_datepickers(self, field):
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
        self.assertEquals(True, hasattr(decision, "status"), 
                          "Decision does not have a status")
        
    def test_decision_model_has_watchers(self):
        decision_model = self.create_and_return_decision()
        self.assertTrue(hasattr(decision_model, "watchers"), 
                          "Decision does not have watchers")
                
    def test_decision_form_omits_watchers(self):
        decision_form = DecisionForm()
        self.assertTrue("watcher" not in decision_form.fields,
                          "Decision form should not contain watchers")

    def test_add_decision_web_post_updates_watchers(self):
        post_dict = self.get_default_decision_form_dict()
        post_dict.update({'description': 'Make Eggs',
                            'watch': True })
        
        self.client.post(reverse('publicweb_decision_create', args=[0]), 
                                post_dict,
                                follow=True )

        decision = Decision.objects.all()[0]
        self.assertEqual(1, len(decision.watchers.all()), "Expected one watcher only.")        
        self.assertEqual(self.user, decision.watchers.all()[0], "User not added to watcher list during add")
        
    def test_edit_decision_web_post_updates_watchers(self):
        decision = self.create_and_return_decision()
        
        post_dict = self.get_default_decision_form_dict()
        post_dict.update({'description': 'Make Eggs',
                            'watch': True,
                            'feedback_set-TOTAL_FORMS': '3',
                            'feedback_set-INITIAL_FORMS': '0',
                            'feedback_set-MAX_NUM_FORMS': '',
                            'feedback_set-0-description': 'The eggs are bad',
                            'feedback_set-1-description': 'No one wants them'})
        
        self.client.post(reverse('publicweb_decision_update', args=[decision.id]), 
                                post_dict,
                                follow=True )

        decision = Decision.objects.all()[0]
        self.assertEqual(1, len(decision.watchers.all()), "Expected one watcher only.")
        
        self.assertEqual(self.user, decision.watchers.all()[0], "User not added to watcher list during edit")

    def test_form_has_watch(self):
        decision_form = DecisionForm()
        self.assertTrue("watch" in decision_form.fields,
                          "Decision form does not contain watch checkbox")

        self.assertEquals(BooleanField,
                          type(decision_form.fields["watch"]),
                          "Decision form watch is not a BooleanField")
        
        self.assertEquals(CheckboxInput,
                          type(decision_form.fields["watch"].widget),
                          "Decision form watch is not a CheckboxInput widget")


    def test_unwatch(self):
        post_dict = self.get_default_decision_form_dict()
        post_dict.update({  'description': 'Make Eggs',
                            'watch': False,
                            'feedback_set-TOTAL_FORMS': '3',
                            'feedback_set-INITIAL_FORMS': '0',
                            'feedback_set-MAX_NUM_FORMS': '',
                            'feedback_set-0-description': 'The eggs are bad',
                            'feedback_set-1-description': 'No one wants them'})
        
        response = self.client.post(reverse('publicweb_decision_create', args=[0]), 
                                post_dict,
                                follow=True )
        self.assertEqual(1, len(Decision.objects.all()), "Failed to create object" + response.content)
        decision = Decision.objects.all()[0]
        self.assertEqual(0, len(decision.watchers.all()), "watch was deselected!")
        
    def test_add_page_contains_cancel(self):
        path = reverse('publicweb_decision_create', args=[0])
        response = self.client.get(path)
                
        self.assertContains(response, 'type="submit" value="Cancel"', count=1)

    def test_edit_page_contains_cancel(self):
        decision = self.create_and_return_decision()
        path = reverse('publicweb_decision_update', args=[decision.id])
        response = self.client.get(path)
        
        self.assertContains(response, 'type="submit" value="Cancel"', count=1)

    def test_cancel_does_not_add_changes(self):
        post_dict = self.get_default_decision_form_dict()
        post_dict.update({  'description': 'Make Eggs',
                            'watch': False,
                            'submit': "Cancel",
                            'feedback_set-TOTAL_FORMS': '3',
                            'feedback_set-INITIAL_FORMS': '0',
                            'feedback_set-MAX_NUM_FORMS': '',
                            'feedback_set-0-description': 'The eggs are bad',
                            'feedback_set-1-description': 'No one wants them'})        
        
        path = reverse('publicweb_decision_create', args=[0])
        self.client.post(path, post_dict)

        self.assertEqual(0, len(Decision.objects.all()), "Hitting 'Cancel' created an object!")

    def test_cancel_does_not_edit_changes(self):
        decision = self.create_and_return_decision()
        
        post_dict = self.get_default_decision_form_dict()
        post_dict.update({  'description': 'Make Eggs',
                            'watch': False,
                            'submit': "Cancel",
                            'feedback_set-TOTAL_FORMS': '3',
                            'feedback_set-INITIAL_FORMS': '0',
                            'feedback_set-MAX_NUM_FORMS': '',
                            'feedback_set-0-description': 'The eggs are bad',
                            'feedback_set-1-description': 'No one wants them'})        
        
        path = reverse('publicweb_decision_update', args=[decision.id])
        self.client.post(path,
                                post_dict,
                                follow=True )

        decision = Decision.objects.all()[0]
        self.assertEqual("Decision Time", decision.description, "Hitting 'Cancel' created an object!")

    def test_excerpts_is_first_sentence(self):
        decision = self.create_and_return_decision("A.B.C.")
        self.assertEqual(decision.excerpt, "A")
        
        
    
