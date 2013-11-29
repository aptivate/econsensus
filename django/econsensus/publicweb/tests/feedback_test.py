from decision_test_case import DecisionTestCase
from django.core.urlresolvers import reverse
from guardian.shortcuts import assign_perm
from publicweb.forms import FeedbackForm
from django.core import mail
from publicweb.extra_models import FEEDBACK_MAJOR_CHANGES, NotificationSettings
from publicweb.models import Feedback

class FeedbackTest(DecisionTestCase):

    def test_feedback_has_rating(self):
        decision = self.create_and_return_example_decision_with_feedback()

        feedback = decision.feedback_set.all()[0]
        self.assertEquals(True, hasattr(feedback, "rating"), 
                          "Concern does not have a 'rating' attribute")

    def test_email_sent_when_feedback_edited(self):
        decision = self.create_and_return_example_decision_with_feedback()

        settings = NotificationSettings.objects.get(
            user=self.betty, 
            organization=decision.organization
        )
        settings.notification_level = FEEDBACK_MAJOR_CHANGES
        settings.save()
        feedback = decision.feedback_set.all()[0]
        self.assertEqual(feedback.author, self.betty)
        
        # edit feedback, not as author
        self.login(self.charlie)
        assign_perm('edit_decisions_feedback', self.user, self.bettysorg)
        form = FeedbackForm(instance=feedback)
        form.fields['description'] = "New Updated description."
        form.fields['rating'] = 4
        form.fields['resolved'] = False
        form.fields['minor_edit'] = False
        form.fields['watch'] = False
        # Empty the test outbox
        mail.outbox = []
        response = self.client.post(reverse('publicweb_feedback_update',
            args=[feedback.id]), form.fields)
        ##import pdb; pdb.set_trace()
        self.assertEqual(302, response.status_code)
        self.assertEqual(1, len(mail.outbox))


    def test_adding_feedback_with_watch_set_adds_user_as_watcher(self):
        decision = self.create_and_return_decision()
        decision.watchers = []
        decision.save()
        
        # edit feedback, not as author
        self.login(self.charlie)
        assign_perm('edit_decisions_feedback', self.user, self.bettysorg)
        
        data = {'watch': "True",
                'description': "New Updated description.",
                'rating': Feedback.CONSENT_STATUS
                }
        
        self.client.post(reverse('publicweb_feedback_create',
            args=[decision.id]), data)
        
        watchers = [watcher.user for watcher in decision.watchers.all()]
        self.assertIn(self.user, watchers)
        
    def test_adding_feedback_without_watch_set_doesnt_add_user_as_watcher(self):
        decision = self.create_and_return_decision()
        decision.watchers = []
        decision.save()
        
        # edit feedback, not as author
        self.login(self.charlie)
        assign_perm('edit_decisions_feedback', self.user, self.bettysorg)
        
        data = {
                'description': "New Updated description.",
                'rating': Feedback.CONSENT_STATUS
                }

        mail.outbox = []
        self.client.post(reverse('publicweb_feedback_create',
            args=[decision.id]), data)
        
        watchers = [watcher.user for watcher in decision.watchers.all()]
        self.assertNotIn(self.user, watchers)
