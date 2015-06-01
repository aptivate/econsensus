from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.core import mail
from django.core.mail import EmailMessage
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from notification import models as notification
from guardian.shortcuts import assign_perm
from organizations.models import Organization

from publicweb.models import Decision
from decision_test_case import DecisionTestCase
from django.utils import timezone

from publicweb.tests.factories import DecisionFactory, UserFactory, \
        FeedbackFactory, NotificationSettingsFactory, OrganizationUserFactory
from publicweb.extra_models import NotificationSettings, NO_NOTIFICATIONS, \
    MAIN_ITEMS_NOTIFICATIONS_ONLY, FEEDBACK_ADDED_NOTIFICATIONS, \
    FEEDBACK_MAJOR_CHANGES


class NotificationTest(DecisionTestCase):
    """
    This class is used to test django-notification functionality
    """

    def create_settings(self, user, notification_level, organization=None):
        users_organizations = Organization.active.get_for_user(user)
        if not organization:
            organization = users_organizations.latest('id')
        NotificationSettings.objects.create(
            user=user,
            organization=organization,
            notification_level=notification_level
        )

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
        # add a decision
        decision = self.make_decision()
        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)
        all_but_author = decision.organization.users.all()
        self.assertEqual(all_but_author.count(), len(outbox))
        mail_list = self.get_addresses_from_queryset(all_but_author)
        mailed_users = self.get_addresses_from_outbox(outbox)
        self.assertEqual(mailed_users, mail_list)

    def test_change_triggers_notification_if_notification_level_high_enough(self):
        """
        Check that betty gets a mail when charlie makes a change.
        """
        self.create_settings(self.user, FEEDBACK_ADDED_NOTIFICATIONS)
        decision = self.make_decision()
        mail.outbox = []
        other_members = decision.organization.users.exclude(username=self.user.username)
        self.login(other_members[0].username)
        self.update_decision_through_browser(decision.id)

        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)

        mailed_users = self.get_addresses_from_outbox(outbox)
        self.assertIn(self.betty.email, mailed_users)

    def test_change_doesnt_trigger_notification_if_notification_level_too_low(self):
        self.create_settings(self.user, MAIN_ITEMS_NOTIFICATIONS_ONLY)
        decision = self.make_decision()
        mail.outbox = []
        other_members = decision.organization.users.exclude(username=self.user.username)
        self.login(other_members[0].username)
        self.update_decision_through_browser(decision.id)

        outbox = getattr(mail, 'outbox')
        mailed_users = self.get_addresses_from_outbox(outbox)
        self.assertNotIn(self.betty.email, mailed_users)

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

    def test_notifications_sent_to_author(self):
        self.create_decision_through_browser()

        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)

        self.assertIn(self.user.email, self.get_addresses_from_outbox(outbox))

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
        should be sent to all users watching the decision.
        """
        org = self.bettysorg
        [
            NotificationSettingsFactory(
                user=user,
                organization=org,
                notification_level=FEEDBACK_ADDED_NOTIFICATIONS
            ) for user in org.users.all()
        ]
        decision = self.make_decision(organization=org)
        mail.outbox = []
        all_members = decision.organization.users.all().exclude(username=self.user.username)
        self.login(all_members[0].username)
        self.create_feedback_through_browser(decision.id)
        outbox = getattr(mail, 'outbox')
        outbox_to = [to for to_list in outbox for to in to_list.to]
        user_list = [user_object.email for user_object in decision.organization.users.exclude(is_active=False)]
        self.assertItemsEqual(user_list, outbox_to)

    def test_new_comment_notification(self):
        """
        When a new comment is added to feedback notifcations
        should be sent to all users watching the decision.
        """
        [
            NotificationSettingsFactory(
                user=user,
                organization=self.bettysorg,
                notification_level=FEEDBACK_MAJOR_CHANGES
            ) for user in self.bettysorg.users.all()
        ]
        decision = self.make_decision(organization=self.bettysorg)
        feedback = self.make_feedback(decision=decision)
        mail.outbox = []
        feedback_type = ContentType.objects.get(app_label="publicweb", model="feedback")
        comment = self.make_comment(user=self.user,
                                    content_object=feedback,
                                    object_pk=feedback.id,
                                    content_type=feedback_type,
                                    submit_date=timezone.now(),
                                    site=Site.objects.get_current())
        outbox = getattr(mail, 'outbox')
        outbox_to = [to for to_list in outbox for to in to_list.to]
        all_members = comment.content_object.decision.organization.users.exclude(is_active=False)
        user_list = [user_object.email for user_object in all_members]
        self.assertItemsEqual(user_list, outbox_to)

    def test_emails_come_from_organization(self):
        users_orgs = Organization.active.get_for_user(self.user)
        self.create_settings(self.user, FEEDBACK_ADDED_NOTIFICATIONS,
             users_orgs[0])
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
            content_object=feedback,
            object_pk=feedback.id,
            content_type=feedback_type)
        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)
        self.assertEqual(outbox[0].from_email, comment.content_object.decision.get_email())
        mail.outbox = []
        """# Edit the comment
        Editing comments is not supported at this time
        comment.decision = "edited"
        comment.save()
        self.send_comment_posted_signal(comment=comment)
        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)
        self.assertEqual(outbox[0].from_email, comment.content_object.decision.get_email())"""
        mail.outbox = []
        # Add Decision for second organization
        self.create_settings(self.user, FEEDBACK_ADDED_NOTIFICATIONS,
             users_orgs[1])
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
        self.assertEqual(
            outbox[0].extra_headers['References'],
            " ".join(
                [feedback.decision.get_message_id(), feedback.get_message_id()]
            )
        )
        mail.outbox = []

        self.login('charlie')
        assign_perm('edit_decisions_feedback', self.user, self.bettysorg)
        feedback = self.update_feedback_through_browser(feedback.id)
        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)
        self.assertTrue(outbox[0].extra_headers)
        self.assertEqual(outbox[0].extra_headers['Message-ID'], feedback.get_message_id())
        self.assertEqual(outbox[0].extra_headers['In-Reply-To'], feedback.decision.get_message_id())
        self.assertEqual(
            outbox[0].extra_headers['References'],
            " ".join(
                [feedback.decision.get_message_id(), feedback.get_message_id()]
            )
        )

class DecisionNotificationTest(TestCase):
    def setUp(self):
        user = UserFactory()
        self.decision = DecisionFactory(author=user, description="Eat Cheese")
        watcher = UserFactory(email="bob@bobbins.org")
        organization = self.decision.organization
        self.settings = NotificationSettingsFactory(
            user=watcher,
            organization=organization,
            notification_level=FEEDBACK_ADDED_NOTIFICATIONS
        )
        OrganizationUserFactory(user=watcher, organization=organization)

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
                                        author=feedbackAuthor,
                                        editor=feedbackAuthor)
        organization = decision.organization
        self.settings = NotificationSettingsFactory(
            user=self.user,
            organization=organization,
            notification_level=FEEDBACK_MAJOR_CHANGES
        )
        OrganizationUserFactory(user=self.user, organization=organization)

    def test_edit_triggers_email(self):
        mail.outbox = []
        self.feedback.description = "Not so slow"
        self.feedback.save()
        self.assertGreater(len(mail.outbox), 0)

    def test_minor_edit_triggers_no_email(self):
        mail.outbox = []
        self.feedback.description = "Not too fast"
        self.feedback.minor_edit = True
        self.feedback.save()
        self.assertEqual(len(mail.outbox), 0)

    # It is an arguable point whether this logic should be in the UI
    # or the back end. However, whilst it's in the latter, we'll have a
    # test for it here.
    def test_minor_edit_by_non_author_triggers_email(self):
        mail.outbox = []
        self.feedback.description = "Not so quick"
        self.feedback.minor_edit = True
        self.feedback.editor = UserFactory(email="hob@bobbins.org")
        self.feedback.save()
        self.assertGreater(len(mail.outbox), 0)
