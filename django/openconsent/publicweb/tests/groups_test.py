#-*- coding: utf-8 -*-

"""
Tests for the public website part of the OpenConsent project
"""
from django.test import TestCase
from django.core.urlresolvers import reverse

from openconsent.publicweb.models import Group
from openconsent.publicweb.forms import GroupForm

class GroupsTest(TestCase):
    def test_get_list_of_groups(self):
        """
        Test the list of all decision groups is included in the page context.
        """
        response = self.client.get(reverse('groups'))
        self.assertEqual(list(Group.objects.all()),
        list(response.context['groups']))
        
    def test_add_group_link_appears_on_groups_page(self):
        
        path = reverse('groups')
        response = self.client.get(path)
        add_path = reverse('group_add')
        self.assertContains(response,
                            "<a href=\"" + add_path + "\">Add Group</a>")
    
    def test_add_group_goes_to_empty_edit_form(self):
        
        path = reverse('group_add')
        response = self.client.get(path)

        form = GroupForm()
        self.assertEqual(form.as_p(),
            response.context['group_form'].as_p())

    def test_group_add_page_rejects_empty_submit(self):
        
        form = GroupForm({'short_name':''})
        self.assertFalse(form.is_valid())   # validates the form and adds error messages
        
        path = reverse('group_add')
        response = self.client.post(path, {'short_name':''})
        
        self.assertEqual(form.as_p(),
            response.context['group_form'].as_p())
        
    def test_group_add_adds_database_entry(self):
               
        path = reverse('group_add')
        response = self.client.post(path, {'short_name':'Breakfast'})
        
        group_entry = Group.objects.all()[0]
        
        self.assertEqual('Breakfast', group_entry.short_name)
        
    def test_group_add_redirects_to_group_display_page(self):
        
        path = reverse('group_add')
        response = self.client.post(path, {'short_name':'Breakfast'})
                
        self.assertRedirects(response, reverse('groups'))
        