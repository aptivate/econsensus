from django.test.testcases import SimpleTestCase
from publicweb.extra_models import (NotificationSettings, OrganizationSettings,
    NO_NOTIFICATIONS, MAIN_ITEMS_NOTIFICATIONS_ONLY)
from django.contrib.auth.models import User, AnonymousUser
from organizations.models import Organization
from django.db.models.fields.related import OneToOneField
from publicweb.tests.factories import UserFactory, OrganizationFactory
from mock import patch, MagicMock
from django.test.client import RequestFactory
from publicweb.views import UserNotificationSettings
from publicweb.forms import NotificationSettingsForm
from django.core.urlresolvers import reverse
from dbsettings.models import Root
from django.http import HttpResponseRedirect

def create_fake_organization(**kwargs):
    return OrganizationFactory.build(**kwargs)
   
        
class SettingsTest(SimpleTestCase):
    def test_notification_settings_have_user_field(self):
        self.assertTrue(hasattr(NotificationSettings, 'user'))        
        
    def test_notification_settings_are_linked_to_user(self):
        self.assertEqual(NotificationSettings.user.field.rel.to, User)
    
    def test_notification_settings_have_organization_field(self):
        self.assertTrue(hasattr(NotificationSettings, 'organization'))
        
    def test_notification_settings_are_linked_to_organization(self):
        self.assertEqual(
          NotificationSettings.organization.field.rel.to, Organization)
    
    def test_organization_settings_have_organization_field(self):
        self.assertTrue(hasattr(OrganizationSettings, 'organization'))
    
    def test_organization_settings_are_linked_to_organization(self):
        self.assertEqual(
          OrganizationSettings.organization.field.rel.to, Organization)
    
    def test_each_organization_has_only_one_set_of_settings(self):
        self.assertIsInstance(
          OrganizationSettings.organization.field, OneToOneField)
    
    def test_notification_settings_are_unique_for_an_organization_and_user(self):
        self.assertEqual((('user', 'organization'),),
          NotificationSettings()._meta.unique_together)
    
    def test_notifitication_settings_default_value_is_main_items_only(self):
        the_settings = NotificationSettings() 
        self.assertEqual(MAIN_ITEMS_NOTIFICATIONS_ONLY, 
         the_settings.notification_level)
    
    @patch('publicweb.views.Organization.objects', 
           new=MagicMock(
                 spec=Organization.objects,
                 get=create_fake_organization,
                 filter=create_fake_organization
           )
    )
    def test_notification_settings_view_uses_a_form(self):
        user = UserFactory.build(id=1)
        organization = create_fake_organization(id=2)
        
        request = RequestFactory().get('/')
        request.user = user
        
        context = UserNotificationSettings.as_view()(
                      request, 
                      organization=organization.id
        ).context_data
    
        self.assertIn('form', context)
    
    def test_notifcation_settings_view_redirects_to_organization_list(self):
        notification_settings_view = UserNotificationSettings()
        self.assertEqual(reverse('organization_list'), 
             notification_settings_view.get_success_url())
    
    def test_user_notification_settings_view_context_contains_organisation(self):
        notification_settings_view = UserNotificationSettings()
        
        notification_settings_view.object = MagicMock(spec=NotificationSettings)
        notification_settings_view.organization = create_fake_organization(id=2)
        context = notification_settings_view.get_context_data()
        self.assertIn('organization', context)
        self.assertTrue(context['organization'])
    
    @patch('publicweb.views.Organization.objects', 
           new=MagicMock(
                 spec=Organization.objects,
                 get=create_fake_organization,
                 filter=create_fake_organization
           )
    )
    def test_notification_settings_view_uses_notification_settings_form(self):
        user = UserFactory.build(id=1)
        organization = create_fake_organization(id=2)
        
        request = RequestFactory().get('/')
        request.user = user

        context = UserNotificationSettings.as_view()(
                        request,
                        organization=organization.id
        ).context_data
        
        self.assertIsInstance(context['form'], NotificationSettingsForm)
    
    def test_notification_settings_view_requires_login(self):
        request = RequestFactory().get('/')
        
        user = AnonymousUser()
        
        organization = create_fake_organization(id=2)
        
        request.user = user
        
        response = UserNotificationSettings.as_view()(request,
             organization=organization.id)
        
        self.assertIsInstance(response, HttpResponseRedirect)
    
    @patch('publicweb.views.Organization.objects', 
           new=MagicMock(
                spec=Organization.objects,
                get=create_fake_organization,
                filter=create_fake_organization
           )
    )
    @patch('publicweb.views.UserNotificationSettings.model',
           return_value=MagicMock(
                spec=NotificationSettings,
                _meta=MagicMock(fields=[], many_to_many=[]),
                root_id=None
           )
    )
    def test_posting_valid_data_saves_settings(self, settings_obj):
        organization = create_fake_organization(id=2)
        
        request = RequestFactory().post(
            reverse('notification_settings', args=[organization.id]), 
            {'notification_level': unicode(NO_NOTIFICATIONS)}
        )
        
        user = UserFactory.build(id=1)
        request.user = user
        
        # This patch depends on the UsertNotificationSettings.model patch 
        # It needs to return the object created by that patch, which is passed 
        # in as a parameter.
        # The only way I've found to handle the dependency is to do this patch
        # here
        with patch('publicweb.views.UserNotificationSettings.model.objects',
                   get=lambda organization, user: settings_obj):
            UserNotificationSettings.as_view()(
                request, 
                organization=organization.id
            )
        
        self.assertTrue(settings_obj.save.called)
    
    @patch('publicweb.views.Organization.objects', 
           new=MagicMock(
                spec=Organization.objects,
                get=create_fake_organization,
                filter=create_fake_organization
           )
    )
    @patch('publicweb.views.UserNotificationSettings.model',
           return_value=MagicMock(
                spec=NotificationSettings,
                _meta=MagicMock(fields=[], many_to_many=[]),
                root_id=None
           )
    )
    def test_posting_invalid_data_returns_form_with_errors(self, settings_obj):        
        user = UserFactory.build(id=1)
        organization = create_fake_organization(id=2)
        
        request = RequestFactory().post(
            reverse('notification_settings', args=[organization.id]))
        
        request.user = user
        
        # This patch depends on the UsertNotificationSettings.model patch 
        # It needs to return the object created by that patch, which is passed 
        # in as a parameter.
        # The only way I've found to handle the dependency is to do this patch
        # here
        with patch('publicweb.views.UserNotificationSettings.model.objects',
                   get=lambda organization, user: settings_obj):
            response = UserNotificationSettings.as_view()(
                request, 
                organization=organization.id
            )
            
        self.assertIn('form', response.context_data)
        self.assertTrue(response.context_data['form'].errors)
    
    @patch('publicweb.views.Organization.objects', 
           new=MagicMock(
                spec=Organization.objects,
                get=create_fake_organization,
                filter=create_fake_organization
           )
    )
    @patch('publicweb.views.UserNotificationSettings.model',
           return_value=MagicMock(
                spec=NotificationSettings,
                _meta=MagicMock(fields=[], many_to_many=[]),
                root_id=None
           )
    )
    def test_cancel_doesnt_save_settings(self, settings_obj):
        user = UserFactory.build(id=1)
        organization = create_fake_organization(id=2)
        
        request = RequestFactory().post(
            reverse('notification_settings', args=[organization.id]), 
            {
                'notification_level': unicode(NO_NOTIFICATIONS),
                'submit': "Cancel"
             }
        )
        
        request.user = user         
        
        # This patch depends on the UsertNotificationSettings.model patch 
        # It needs to return the object created by that patch, which is passed 
        # in as a parameter.
        # The only way I've found to handle the dependency is to do this patch
        # here
        with patch('publicweb.views.UserNotificationSettings.model.objects',
                    get=lambda organization, user: settings_obj):
            UserNotificationSettings.as_view()(
                request, organization=organization.id
            )
                    
        self.assertFalse(settings_obj.save.called)