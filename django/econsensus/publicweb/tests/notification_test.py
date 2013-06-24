from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.core import mail
from django.core.mail import EmailMessage
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from notification import models as notification
from guardian.shortcuts import assign
from organizations.models import Organization

from publicweb.models import Decision
from decision_test_case import DecisionTestCase
from django.utils import timezone

from publicweb.tests.factories import DecisionFactory, UserFactory, \
        FeedbackFactory

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

    def no_emails_to_orig_org_users(self, outbox, orig_org_user_email_set):
        outbox_email_set = set(self.get_addresses_from_outbox(outbox))
        return outbox_email_set.isdisjoint(orig_org_user_email_set)

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
        decision = self.make_decision()
        mail.outbox = []
        other_members = decision.organization.users.exclude(username=self.user.username)
        self.login(other_members[0].username)
        self.update_decision_through_browser(decision.id)

        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)

        mailed_users = self.get_addresses_from_outbox(outbox)
        self.assertIn(self.betty.email, mailed_users)

    def test_changing_new_decisions_org_correct_email_content(self):
        """
        Check that the notification emails states that the Decision
        has changed, not its status (altering Decision via admin 
        screens now sets last_status=status as for user screens).
        """
        orig_org = self.bettysorg
        orig_user = User.objects.get(username="nobbie")
        new_org = Organization.objects.get(name="Ferocious Feral Furrballs")
        self.login(orig_user)
        decision = self.make_decision(organization=orig_org)
        mail.outbox = []
        admin_user = self.change_organization_via_admin_screens(decision, new_org)
        outbox = getattr(mail, 'outbox')
        self.assertEqual(len(outbox), new_org.users.all().count())
        self.assertTrue(orig_user.email not in self.get_addresses_from_outbox(outbox))
        first_email = outbox[0]
        exp_subject_snippet = "] Change to "
        exp_body_snippet = "This is to let you know that %s has changed the " \
            "following item." % admin_user.username
        self.assertTrue(first_email.subject.find(exp_subject_snippet) >= 0)
        self.assertTrue(first_email.body.find(exp_body_snippet) >= 0)

    def test_changing_decisions_org_alters_watchers(self):
        """
        If a Decision's Organization is changed, ensure that members of the 
        orig Organization no longer get email notifications about it. 
        Check that all current members of the new Organization do get notified 
        appropriately upon changes to the Decision, its Feedbacks, and all of 
        their Comments.
        To avoid hiding bugs in who gets what notification, use a different 
        user per action (some actions only prompt notification to the 
        author)
        """
        orig_org = self.bettysorg
        new_org = Organization.objects.get(name="Ferocious Feral Furrballs")
        # TODO: deduce suitable members to use rather than hardcoding and then asserting suitability
        orig_org_members_names = ['nobbie', 'ollie', 'pollie', 'queenie', 'robbie']
        orig_org_members_users = [User.objects.get(username=name) for name in orig_org_members_names]
        orig_org_user_email_set = set([user.email for user in orig_org_members_users])
        orig_org_members = dict(zip(orig_org_members_names, orig_org_members_users))
        new_org_members_names = ['andy', 'betty', 'charlie', 'debbie', 'ernie']
        new_org_members_users = [User.objects.get(username=name) for name in new_org_members_names]
        new_org_members = dict(zip(new_org_members_names, new_org_members_users))
        new_org_members_count = new_org.users.all().count()
        for user in orig_org_members.values():
            self.assertTrue(orig_org.is_member(user))
            self.assertFalse(new_org.is_member(user))
            assign('edit_decisions_feedback', user, orig_org)
        for user in new_org_members.values():
            self.assertTrue(orig_org.is_member(user))
            self.assertTrue(new_org.is_member(user))
            assign('edit_decisions_feedback', user, new_org)

        # Make a decision under original org and edit it in various
        # ways using various users 
        self.login(orig_org_members['nobbie'])
        decision = self.make_decision(organization=orig_org)
        self.login(orig_org_members['ollie'])
        self.update_decision_through_browser(
            decision.id, 
            description=decision.description + ' updated')
        self.login(orig_org_members['pollie'])
        feedback = self.make_feedback(decision=decision)
        self.login(orig_org_members['queenie'])
        self.update_feedback_through_browser(
            feedback.id,
            description = feedback.description + ' updated')
        self.login(orig_org_members['robbie'])
        comment = self.make_comment(
            object_pk=feedback.id,
            content_type=ContentType.objects.get(name='feedback')) 
        mail.outbox = []

        # Move the decision to the new org
        # TODO: we should send a special notification to the original
        # org users telling them of the move (see 
        # https://aptivate.kanbantool.com/boards/5986-econsensus#tasks-1533249)
        self.change_organization_via_admin_screens(decision, new_org)
        outbox = getattr(mail, 'outbox')
        self.assertEqual(len(outbox), new_org_members_count)
        self.assertTrue(self.no_emails_to_orig_org_users(outbox, orig_org_user_email_set))
        mail.outbox = []

        # Edit the decision in various ways using various users of the 
        # new organization 
        self.login(new_org_members['andy'])
        self.update_decision_through_browser(
            decision.id, 
            description=decision.description + ' updated again')
        outbox = getattr(mail, 'outbox')
        self.assertEqual(len(outbox), new_org_members_count)
        self.assertTrue(self.no_emails_to_orig_org_users(outbox, orig_org_user_email_set))
        mail.outbox = []

        self.login(new_org_members['betty'])
        self.update_feedback_through_browser(
            feedback.id, 
            description=feedback.description+' updated again')
        outbox = getattr(mail, 'outbox')
        self.assertEqual(len(outbox), new_org_members_count)
        self.assertTrue(self.no_emails_to_orig_org_users(outbox, orig_org_user_email_set))
        mail.outbox = []

        # Can't edit Comments via screens yet, but lets check that 
        # we've future proofed for this
        self.login(new_org_members['charlie'])
        comment.comment += ' updated'
        comment.save()
        outbox = getattr(mail, 'outbox')
        self.assertEqual(len(outbox), new_org_members_count)
        self.assertTrue(self.no_emails_to_orig_org_users(outbox, orig_org_user_email_set))
        mail.outbox = []

        self.login(new_org_members['debbie'])
        feedback_2 = self.make_feedback(decision=decision)
        outbox = getattr(mail, 'outbox')
        # New feedback prompts notifications to all watchers of decision minus 
        # the feedback author
        self.assertEqual(len(outbox), new_org_members_count - 1)
        self.assertTrue(self.no_emails_to_orig_org_users(outbox, orig_org_user_email_set))
        mail.outbox = []

        self.login(new_org_members['ernie'])
        comment_2 = self.make_comment(
            object_pk=feedback.id,
            content_type=ContentType.objects.get(name='feedback')) 
        outbox = getattr(mail, 'outbox')
        # New comment prompts notification to all watchers of decision minus 
        # the comment author
        self.assertEqual(len(outbox), new_org_members_count - 1)
        self.assertTrue(self.no_emails_to_orig_org_users(outbox, orig_org_user_email_set))
        
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
        user_list = [user_object.email for user_object in decision.organization.users.exclude(username=self.user).exclude(is_active=False)]
        self.assertNotIn(self.user.email, outbox_to)
        self.assertItemsEqual(user_list, outbox_to)

    def test_new_comment_notification(self):
        """
        When a new comment is added to feedback notifcations
        should be sent to all users watching the decision,
        minus the author of the new comment.
        """
        decision = self.make_decision(organization=self.bettysorg)
        feedback = self.make_feedback(decision=decision)
        mail.outbox = []
        feedback_type = ContentType.objects.get(app_label="publicweb", model="feedback")
        comment = self.make_comment(user=self.user,
                                    content_object=feedback, 
                                    object_pk=feedback.id,
                                    content_type=feedback_type,
                                    submit_date = timezone.now(),
                                    site = Site.objects.get_current())
        outbox = getattr(mail, 'outbox')
        outbox_to = [to for to_list in outbox for to in to_list.to]
        all_members = comment.content_object.decision.organization.users.exclude(username=self.user).exclude(is_active=False) 
        user_list = [user_object.email for user_object in all_members]
        self.assertNotIn(self.user.email, outbox_to)
        self.assertItemsEqual(user_list, outbox_to)
        
    def test_changed_feedback_notification(self):
        """
        When feedback is changed only the original author of the feedback
        should be notified.
        """
        # Betty creates a decision
        decision = self.create_decision_through_browser()
        # Charlie adds feedback to it
        self.login('charlie')
        assign('edit_decisions_feedback', self.user, self.bettysorg)        
        feedback = self.create_feedback_through_browser(decision.id)
        mail.outbox = []
        # Betty changes the feedback...
        self.login('betty')
        assign('edit_decisions_feedback', self.user, self.bettysorg)        
        self.update_feedback_through_browser(feedback.id)
        # Check email
        outbox = getattr(mail, 'outbox')
        outbox_to = [to for to_list in outbox for to in to_list.to]
        user_list = [self.charlie.email]
        self.assertItemsEqual(user_list, outbox_to)
        
    def test_emails_come_from_organization(self):
        users_orgs = Organization.active.get_for_user(self.user)
        self.assertGreaterEqual(len(users_orgs), 2)
        # Add Decision for first organization
        decision = self.make_decision(organization=users_orgs[0])
        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)
        self.assertEqual(outbox[0].from_email, decision.get_email())
        mail.outbox = []
        # Edit Decision
        decision = self.update_decision_through_browser(decision.id)
        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)
        self.assertEqual(outbox[0].from_email, decision.get_email())
        mail.outbox = []
        # Add a Feedback
        feedback = self.make_feedback(author=self.charlie, decision=decision)
        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)
        self.assertEqual(outbox[0].from_email, feedback.decision.get_email())
        mail.outbox = []
        # Edit the Feedback
        feedback = self.update_feedback_through_browser(feedback.id)
        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)
        self.assertEqual(outbox[0].from_email, feedback.decision.get_email())
        mail.outbox = []
        # Add a comment
        feedback_type = ContentType.objects.get(app_label="publicweb", model="feedback")
        comment = self.make_comment(user=self.charlie,
            content_object = feedback,
            object_pk = feedback.id,
            content_type = feedback_type) 
        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)
        self.assertEqual(outbox[0].from_email, comment.content_object.decision.get_email())
        mail.outbox = []
        # Edit the comment
        comment.decision = "edited"
        comment.save()
        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)
        self.assertEqual(outbox[0].from_email, comment.content_object.decision.get_email())
        mail.outbox = []
        # Add Decision for second organization
        decision = self.make_decision(organization=users_orgs[1])
        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)
        self.assertEqual(outbox[0].from_email, decision.get_email())
        
    def test_emails_contain_extra_header_info(self):
        users_orgs = Organization.active.get_for_user(self.user)
        self.assertGreaterEqual(len(users_orgs), 2)
        decision = self.make_decision(organization=users_orgs[0])
        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)
        self.assertTrue(outbox[0].extra_headers)
        self.assertEqual(outbox[0].extra_headers['Message-ID'], decision.get_message_id())
        mail.outbox = []

        decision = self.update_decision_through_browser(decision.id)
        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)
        self.assertTrue(outbox[0].extra_headers)
        self.assertEqual(outbox[0].extra_headers['Message-ID'], decision.get_message_id())
        mail.outbox = []

        feedback = self.create_feedback_through_browser(decision.id)
        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)
        self.assertTrue(outbox[0].extra_headers)
        self.assertEqual(outbox[0].extra_headers['Message-ID'], feedback.get_message_id())
        self.assertEqual(outbox[0].extra_headers['In-Reply-To'], feedback.decision.get_message_id())
        mail.outbox = []
        
        self.login('charlie')
        assign('edit_decisions_feedback', self.user, self.bettysorg)        
        feedback = self.update_feedback_through_browser(feedback.id)
        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)
        self.assertTrue(outbox[0].extra_headers)
        self.assertEqual(outbox[0].extra_headers['Message-ID'], feedback.get_message_id())
        self.assertEqual(outbox[0].extra_headers['In-Reply-To'], feedback.decision.get_message_id())

class DecisionNotificationTest(TestCase):
    def setUp(self):
        user = UserFactory()
        self.decision = DecisionFactory(author=user, description="Eat Cheese")
        watcher = UserFactory(email="bob@bobbins.org")
        notification.observe(self.decision, watcher, 'decision_change')

    def test_edit_triggers_email(self):
        mail.outbox = []
        self.decision.description = "Make Cheese"
        self.decision.save()
        self.assertGreater(len(mail.outbox), 0)

    def test_minor_edit_triggers_no_email(self):
        mail.outbox = []
        self.decision.description = "Eat Cheese!"
        self.decision.minor_edit = True
        self.decision.save()
        self.assertEqual(len(mail.outbox), 0)

class FeedbackNotificationTest(TestCase):
    def setUp(self):
        mail.outbox = []
        self.user = UserFactory(email="bob@bobbins.org")
        decision = DecisionFactory(author=self.user)
        feedbackAuthor = UserFactory(email="rob@bobbins.org")
        self.feedback = FeedbackFactory(decision=decision,
                                        description="Not so fast",
                                        author=feedbackAuthor)

    def test_edit_triggers_email(self):
        mail.outbox = []
        self.feedback.description = "Not so slow"
        self.feedback.save()
        self.assertGreater(len(mail.outbox), 0)
