from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse

from organizations.models import Organization

from publicweb.models import Decision
from decision_test_case import DecisionTestCase

class NotificationTest(DecisionTestCase):
    """
    This class is used to test django-notification functionality
    """
    def get_addresses_from_outbox(self, outbox):
        return_list = list()
        for thismail in outbox:
            user = User.objects.get(email=thismail.to[0])
            return_list.append(user.email)
        return return_list

    def get_addresses_from_queryset(self, queryset):
        return_list = list()
        for this in queryset:
            return_list.append(this.email)        
        return return_list
        
    def test_send_locmem_email(self):
        """
        Tests that django can send an email through the locmem backend
        """
        
        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

        msg = EmailMessage('X', 'Y', 'a@b.c', ['x@y.z'])
        msg.send()
        
        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)
        
        self.assertEqual(msg, outbox[0])
                
    def test_create_triggers_notification(self):
        #add a decision
        decision = self.make_decision()
        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)
        all_but_author = decision.organization.users.all()
        self.assertEqual(all_but_author.count(), len(outbox))
        mail_list = self.get_addresses_from_queryset(all_but_author)
        mailed_users = self.get_addresses_from_outbox(outbox)
        self.assertEqual(mailed_users, mail_list)

    def test_change_triggers_notification(self):
        """
        Check that betty gets a mail when charlie makes a change.
        """
        decision = self.create_decision_through_browser()
        mail.outbox = []
        self.login('charlie')
        self.update_decision_through_browser(decision.id)

        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)

        mailed_users = self.get_addresses_from_outbox(outbox)
        self.assertIn(self.betty.email, mailed_users)
        
    def test_notifications_dont_contain_amp(self):
        """
        We want to verify that the notifications sent out do not contain
        confusing text like '&amp' instead of '&' or ''&lt'
        instead of '<'
        
        All plaintext emails should be marked 'safe' in the Django template.
        """
        self.make_decision(description='&', author=self.user, editor=self.user)
        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)
                
        self.assertNotIn('&amp', outbox[0].subject)
        self.assertNotIn('&amp', outbox[0].body)
        
    def test_notifications_not_sent_to_author(self):
        """
        We want to make sure that when a user creates or changes an 
        item they are not sent a notification. The message goes to those
        that do not already know the item has changed!
        """        
        self.create_decision_through_browser()

        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)

        self.assertNotIn(self.user, self.get_addresses_from_outbox(outbox))
        
    def test_emails_not_sent_to_inactive_users(self):
        self.charlie.is_active = False
        self.charlie.save()
        self.create_decision_through_browser()
        outbox = getattr(mail, 'outbox')
        outbox_to = [x.to for x in outbox]
        self.assertNotIn(self.charlie.email, outbox_to)

    def test_new_feedback_notification(self):
        """
        When new feedback is added to a decision notifcations
        should be sent to all users watching the decision
        minus the author of the new feedback.
        """
        org = self.bettysorg
        decision = self.make_decision(organization=org)
        mail.outbox = []        
        all_members = decision.organization.users.all().exclude(username=self.user.username)
        self.login(all_members[0].username)
        self.create_feedback_through_browser(decision.id)
        outbox = getattr(mail, 'outbox')
        outbox_to = [to for to_list in outbox for to in to_list.to]
        user_list = [user_object.email for user_object in decision.organization.users.exclude(username=self.user)]
        self.assertNotIn(self.user.email, outbox_to)
        self.assertItemsEqual(user_list, outbox_to)
        
    def test_changed_feedback_notification(self):
        """
        When feedback is changed only the original author of the feedback
        should be notified.
        """
        decision = self.create_decision_through_browser()
        #charlie adds feedback
        self.login('charlie')
        feedback = self.create_feedback_through_browser(decision.id)
        mail.outbox = []
        #Charlie changes the feedback...
        self.login('charlie')
        self.update_feedback_through_browser(feedback.id)
        outbox = getattr(mail, 'outbox')
        outbox_to = [to for to_list in outbox for to in to_list.to]
        user_list = [self.charlie.email]
        self.assertItemsEqual(user_list, outbox_to)
        
    def test_emails_come_from_organization(self):
        users_orgs = Organization.active.get_for_user(self.user)
        self.assertGreaterEqual(len(users_orgs), 2)
        decision = self.make_decision(organization=users_orgs[0])
        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)
        self.assertEqual(outbox[0].from_email, decision.get_email())
        mail.outbox = []
        decision = self.make_decision(organization=users_orgs[1])
        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)
        self.assertEqual(outbox[0].from_email, decision.get_email())
        