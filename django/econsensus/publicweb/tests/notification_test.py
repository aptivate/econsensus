from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import AdminSite
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from guardian.shortcuts import assign
from organizations.models import Organization

from publicweb.models import Decision
from decision_test_case import DecisionTestCase
from django.utils import timezone

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

    def change_organization_via_admin_screens(self, decision, new_organization):
        orig_user = self.user

        admin_user = User.objects.filter(is_staff=True)[0]
        self.login(admin_user.username)
        ma = ModelAdmin(Decision, AdminSite())
        data = ma.get_form(None)(instance=decision).initial
        for key, value in data.items():
            if value == None:
                data[key] = u''
        man_data = {
            'feedback_set-TOTAL_FORMS': u'1', 
            'feedback_set-INITIAL_FORMS': u'0', 
            'feedback_set-MAX_NUM_FORMS': u''
        }
        data.update(man_data)
        data['organization'] = new_organization.id
        url = reverse('admin:publicweb_decision_change', args=[decision.id])
        response = self.client.post(url, data, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Decision.objects.get(id=decision.id).organization.id, new_organization.id)

        self.login(orig_user)
        
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

    def test_changing_decisions_org_drops_decisions_watchers(self):
        """
        If a Decision's Organization is changed, ensure that members of 
        the old Organization no longer get email notifications about it.
        """
        orig_org = self.bettysorg
        new_org = Organization.objects.get(name="Ferocious Feral Furrballs")
        orig_org_members_names = ['nobbie', 'ollie', 'pollie', 'queenie', 'robbie']
        orig_org_members_users = [User.objects.get(username=name) for name in orig_org_members_names]
        orig_org_members = dict(zip(orig_org_members_names, orig_org_members_users))
        both_org_members_names = ['andy', 'betty', 'charlie', 'debbie', 'ernie', 'freddy']
        both_org_members_users = [User.objects.get(username=name) for name in both_org_members_names]
        both_org_members = dict(zip(both_org_members_names, both_org_members_users))
        from guardian.shortcuts import assign
        for user in orig_org_members.values():
            self.assertTrue(orig_org.is_member(user))
            self.assertFalse(new_org.is_member(user))
            assign('edit_decisions_feedback', user, orig_org)
        for user in both_org_members.values():
            self.assertTrue(orig_org.is_member(user))
            self.assertTrue(new_org.is_member(user))
            assign('edit_decisions_feedback', user, orig_org)
            assign('edit_decisions_feedback', user, new_org)
        import copy
        new_org_members = copy.deepcopy(both_org_members)
        new_org_members.update(orig_org_members)


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

        
        self.change_organization_via_admin_screens(decision, new_org)
        outbox = getattr(mail, 'outbox')
        self.assertEqual(len(outbox), 0)

        self.login(new_org_members['andy'])
        self.update_decision_through_browser(
            decision.id, 
            description=decision.description + ' updated again')
        # This adds andy to the decision's watcher list
        # TODO: is above a bug?
        outbox = getattr(mail, 'outbox')
        self.assertEqual(len(outbox), 1)
        self.assertEqual(outbox[0].to[0], new_org_members['andy'].email)
        mail.outbox = []

        self.login(new_org_members['betty'])
        self.update_feedback_through_browser(
            feedback.id, 
            description=feedback.description+' updated again')
        # This adds betty to the decision's watcher list.
        outbox = getattr(mail, 'outbox')
        self.assertEqual(len(outbox), 0)

        # Can't edit Comments via screens yet, but lets future proof:
        self.login(new_org_members['charlie'])
        comment.comment += ' updated'
        comment.save()
        outbox = getattr(mail, 'outbox')
        # TODO: fix this
        self.assertEqual(len(outbox), 1)
        self.assertEqual(outbox[0].to[0], orig_org_members['robbie'].email)
        mail.outbox = []

        self.login(new_org_members['debbie'])
        feedback_2 = self.make_feedback(decision=decision)
        outbox = getattr(mail, 'outbox')
        recipient_addresses = self.get_addresses_from_outbox(outbox)
        self.assertEqual(len(recipient_addresses), 2)
        self.assertTrue(new_org_members['andy'].email in recipient_addresses)
        self.assertTrue(new_org_members['betty'].email in recipient_addresses)
        mail.outbox = []

        self.login(new_org_members['ernie'])
        comment_2 = self.make_comment(
            object_pk=feedback.id,
            content_type=ContentType.objects.get(name='feedback')) 
        outbox = getattr(mail, 'outbox')
        recipient_addresses = self.get_addresses_from_outbox(outbox)
        self.assertEqual(len(recipient_addresses), 2)
        self.assertTrue(new_org_members['andy'].email in recipient_addresses)
        self.assertTrue(new_org_members['betty'].email in recipient_addresses)
        
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
