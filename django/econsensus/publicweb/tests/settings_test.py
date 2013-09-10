from django.test.testcases import SimpleTestCase
from publicweb.models import (NotificationSettings, OrganizationSettings,\
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

def get_organization(**kwargs):
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
    
    def test_user_notification_settings_view_uses_a_form(self):
        notification_settings_view = UserNotificationSettings()
        notification_settings_view.object = MagicMock(spec=NotificationSettings)
        notification_settings_view.object._meta.fields = []
        notification_settings_view.object._meta.many_to_many = []
        
        user = UserFactory.build(id=1)
        organization = get_organization()
        
        organization_objects = MagicMock(Organization.objects)
        organization_objects.get = get_organization
        organization_objects.filter = get_organization
        
        with patch('publicweb.views.Organization.objects', 
                   new=organization_objects):
            request = RequestFactory().get('/')
            request.user = user
            notification_settings_view.request = request
            context = notification_settings_view.dispatch(request, 
              organization=organization.id).context_data

        self.assertIn('form', context)
    
    def test_user_notifcation_settings_view_redirects_to_organization_list(self):
        notification_settings_view = UserNotificationSettings()
        self.assertEqual(reverse('organization_list'), 
             notification_settings_view.get_success_url())
        
    def test_user_notification_settings_view_uses_user_notification_settings_form(self):
        notification_settings_view = UserNotificationSettings()
        notification_settings_view.object = MagicMock(spec=NotificationSettings)
        
        user = UserFactory.build(id=1)
        organization = get_organization()
        
        organization_objects = MagicMock(Organization.objects)
        organization_objects.get = get_organization
        organization_objects.filter = get_organization
        
        with patch('publicweb.views.Organization.objects', 
                   new=organization_objects):
            request = RequestFactory().get('/')
            request.user = user
            notification_settings_view.request = request
            context = notification_settings_view.dispatch(request,
             organization=organization.id).context_data
        
        self.assertIsInstance(context['form'], NotificationSettingsForm)
    
    def test_notification_settings_view_requires_login(self):
        notification_settings_view = UserNotificationSettings()
        request = RequestFactory().get('/')
        
        user = AnonymousUser()
        
        organization = get_organization()
        
        request.user = user
        
        response = notification_settings_view.dispatch(request,
             organization=organization.id)
        
        self.assertIsInstance(response, HttpResponseRedirect)
    
    def test_post_valid_data_saves_settings(self):
        notification_settings_view = UserNotificationSettings()
        
        user = UserFactory.build(id=1)
        organization = get_organization(id=2)
        
        organization_objects = MagicMock(Organization.objects)
        organization_objects.get = get_organization
        organization_objects.filter = get_organization
        
        meta = MagicMock()
        meta.fields = []
        meta.many_to_many = []
        
        notification_settings = MagicMock(spec=NotificationSettings)
        notification_settings._meta = meta
        notification_settings.root_id = None
        
        def get_settings(**kwargs):
            return notification_settings
        
        notification_settings_objects = MagicMock(NotificationSettings.objects)
        notification_settings_objects.get = get_settings
        
        request = RequestFactory().post(
            reverse('notification_settings', args=[organization.id]), 
            {
             'notification_level': unicode(NO_NOTIFICATIONS)
             })
        
        request.user = user
        notification_settings_view.request = request
        
        org_objects_attribute = 'publicweb.views.Organization.objects'
        settings_view_model = 'publicweb.views.UserNotificationSettings.model'
        settings_view_model_objects = \
            'publicweb.views.UserNotificationSettings.model.objects'
        
        with patch(org_objects_attribute, new=organization_objects):
            with patch(settings_view_model, new=notification_settings) \
                as settings_obj:
                with patch(settings_view_model_objects,
                       new=notification_settings_objects):
                    notification_settings_view.dispatch(request, 
                        organization=organization.id)
                    
        self.assertTrue(settings_obj.save.called)
    
    def test_post_invalid_data_returns_form_with_errors(self):
        notification_settings_view = UserNotificationSettings()
        
        user = UserFactory.build(id=1)
        organization = get_organization(id=2)
        
        organization_objects = MagicMock(Organization.objects)
        organization_objects.get = get_organization
        organization_objects.filter = get_organization
        
        meta = MagicMock()
        meta.fields = []
        meta.many_to_many = []
        
        notification_settings = MagicMock(spec=NotificationSettings)
        notification_settings._meta = meta
        
        def get_settings(**kwargs):
            return notification_settings
        
        notification_settings_objects = MagicMock(NotificationSettings.objects)
        notification_settings_objects.get = get_settings
        
        request = RequestFactory().post(
            reverse('notification_settings', args=[organization.id]))
        
        request.user = user
        notification_settings_view.request = request
        
        org_objects_attribute = 'publicweb.views.Organization.objects'
        settings_view_model = 'publicweb.views.UserNotificationSettings.model'
        settings_view_model_objects = \
            'publicweb.views.UserNotificationSettings.model.objects'
        
        with patch(org_objects_attribute, new=organization_objects):
            with patch(settings_view_model, new=notification_settings):
                with patch(settings_view_model_objects,
                       new=notification_settings_objects):
                    response = notification_settings_view.dispatch(request, 
                    organization=organization.id)
        self.assertIn('form', response.context_data)
        self.assertTrue(response.context_data['form'].errors)
    
    def test_form_valid_method_gives_new_settings_a_root_object(self):
        """
        For some reason, settings classes need a "root_id". 
        This should be added in the form valid method, if it doesn't already
        exist 
        """
        notification_settings_view = UserNotificationSettings()
        
        user = UserFactory.build(id=1)
        organization = get_organization(id=2)
        
        notification_settings_instance = MagicMock(spec=NotificationSettings)
        
        meta = MagicMock()
        meta.fields = []
        meta.many_to_many = []
        
        notification_settings_instance.organisation = organization
        notification_settings_instance.user = user
        notification_settings_instance._meta = meta
        notification_settings_instance.root_id = None
        
        data = {'notification_level': NO_NOTIFICATIONS}
        
        notification_settings_form = NotificationSettingsForm(data,
          instance=notification_settings_instance)
        
        root_objects = MagicMock(spec=Root.objects)
        
        request = RequestFactory().post(
            reverse('notification_settings', args=[organization.id]))
        
        request.user = user
        notification_settings_view.request = request

        with patch('publicweb.views.Root.objects', root_objects) as root:
            notification_settings_view.form_valid(notification_settings_form)
        self.assertTrue(root.create.called)
    
    def test_cancel_doesnt_save_settings(self):
        notification_settings_view = UserNotificationSettings()
        
        user = UserFactory.build(id=1)
        organization = get_organization(id=2)
        
        organization_objects = MagicMock(Organization.objects)
        organization_objects.get = get_organization
        organization_objects.filter = get_organization
        
        meta = MagicMock()
        meta.fields = []
        meta.many_to_many = []
        
        notification_settings = MagicMock(spec=NotificationSettings)
        notification_settings._meta = meta
        notification_settings.root_id = None
        
        def get_settings(**kwargs):
            return notification_settings
        
        notification_settings_objects = MagicMock(NotificationSettings.objects)
        notification_settings_objects.get = get_settings
        
        request = RequestFactory().post(
            reverse('notification_settings', args=[organization.id]), 
            {
             'notification_level': unicode(NO_NOTIFICATIONS),
             'submit': "Cancel"
             })
        
        request.user = user
        notification_settings_view.request = request
        
        org_objects_attribute = 'publicweb.views.Organization.objects'
        settings_view_model = 'publicweb.views.UserNotificationSettings.model'
        settings_view_model_objects = \
            'publicweb.views.UserNotificationSettings.model.objects'
        
        with patch(org_objects_attribute, new=organization_objects):
            with patch(settings_view_model, new=notification_settings) \
                as settings_obj:
                with patch(settings_view_model_objects,
                       new=notification_settings_objects):
                    notification_settings_view.dispatch(request, 
                        organization=organization.id)
                    
        self.assertFalse(settings_obj.save.called)