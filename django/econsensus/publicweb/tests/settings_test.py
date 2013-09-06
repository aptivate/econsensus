from django.test.testcases import SimpleTestCase
from publicweb.models import NotificationSettings, OrganizationSettings,\
    NO_NOTIFICATIONS
from django.contrib.auth.models import User
from organizations.models import Organization
from django.db.models.fields.related import OneToOneField
from publicweb.tests.factories import NotificationSettingsFactory, UserFactory,\
    OrganizationFactory
from mock import Mock, patch
from django.test.client import RequestFactory
from notification.models import ObservedItem
from publicweb.views import UserNotificationSettings

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
    
    def test_user_saved_with_no_notifications_level_has_no_observed_items(self):
        notification_settings_view = UserNotificationSettings()
        
        user = UserFactory.build(id=1)
        organization = OrganizationFactory.build(id=2)
        
        user_objects = Mock(User.objects)
        def get_user(**kwargs):
            return user
        user_objects.get = get_user
        
        organization_objects = Mock(Organization.objects)
        def get_organization(**kwargs):
            return organization
        organization_objects.get = get_organization
        organization_objects.filter = get_organization
        
        
        observed_item = Mock(ObservedItem)
        
        
        notification_settings = Mock(NotificationSettings)
        
        
        request = RequestFactory().post('/', 
            {
             'user': unicode(user.id),
             'organization': unicode(organization.id),
             'notification_level': unicode(NO_NOTIFICATIONS)
             })
        
        request.user = user
        notification_settings_view.request = request
        with patch('django.contrib.auth.models.User.objects', new=user_objects):
            with patch('publicweb.models.Organization.objects', new=organization_objects):
                with patch('notification.models.ObservedItem', new=observed_item):
                    with patch('publicweb.models.NotificationSettings', 
                               new=notification_settings):
                        notification_settings_view.post(request)

        self.assertFalse(observed_item.save.called)
        