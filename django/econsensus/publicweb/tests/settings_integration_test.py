from django.test.testcases import TestCase
from datetime import datetime
from pytz import utc
from publicweb.tests.factories import ObservedItemFactory, NoticeTypeFactory,\
    UserFactory, OrganizationFactory, DecisionFactory,\
    NotificationSettingsFactory
from django.core import mail
from publicweb.models import (NO_NOTIFICATIONS, MAIN_ITEMS_NOTIFICATIONS_ONLY,
    MINOR_CHANGES_NOTIFICATIONS)
from signals.management import DECISION_NEW
from publicweb.observation_manager import ObservationManager

def add_watchers(decision):
    users = UserFactory.create_batch(size=3, email="test@aptivate.org")
    for user in users:
        notice_type = NoticeTypeFactory()
        decision.watchers.add(
              ObservedItemFactory(
                added=datetime.now(utc), 
                user=user, 
                observed_object=decision, 
                notice_type=notice_type
              )
        )
    return decision

class SettingsIntegrationTest(TestCase):
    def test_send_notifications_for_main_items_sends_correct_messages(self):
        initial_count = len(mail.outbox)
        
        number_of_users = 3
        
        organization = OrganizationFactory()
        decision = DecisionFactory(
            organization=organization
        )
        decision = add_watchers(decision)
        
        user1, user2, user3 = UserFactory.create_batch(
            number_of_users, email="test@test.com"
        )

        NotificationSettingsFactory(user=user1, organization=organization, notification_level=NO_NOTIFICATIONS),
        NotificationSettingsFactory(user=user2, organization=organization, notification_level=MAIN_ITEMS_NOTIFICATIONS_ONLY),
        NotificationSettingsFactory(user=user3, organization=organization, notification_level=MINOR_CHANGES_NOTIFICATIONS),

        settings_handler = ObservationManager()
        
        recipients = [user1, user2, user3]
        
        settings_handler.send_notifications(
            recipients, decision, DECISION_NEW, {"observed": decision},
            {
                'Message-ID' : decision.get_message_id(), 
                'Precedence': 'bulk',
                'Auto-Submitted': 'auto-generated'
            },
            "test@me.com"
        )
        
        final_count = len(mail.outbox)
        expected_number_messages_sent = len(decision.watchers.all()) + number_of_users - 1
        actual_number_messages_sent = final_count - initial_count
        
        self.assertEqual(expected_number_messages_sent, actual_number_messages_sent)
