from decision_test_case import DecisionTestCase
from django.core.urlresolvers import reverse
from guardian.shortcuts import assign_perm
from publicweb.forms import FeedbackForm
from publicweb import models
from django.core import mail

class FeedbackTest(DecisionTestCase):

    def test_feedback_has_rating(self):
        decision = self.create_and_return_example_decision_with_feedback()

        feedback = decision.feedback_set.all()[0]
        self.assertEquals(True, hasattr(feedback, "rating"), 
                          "Concern does not have a 'rating' attribute")

    def test_email_sent_when_feedback_edited(self):
        decision = self.create_and_return_example_decision_with_feedback()

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
        # Empty the test outbox
        mail.outbox = []
        response = self.client.post(reverse('publicweb_feedback_update',
            args=[feedback.id]), form.fields)
        ##import pdb; pdb.set_trace()
        self.assertEqual(302, response.status_code)
        self.assertEqual(1, len(mail.outbox))


    def test_no_email_sent_when_feedback_edited_by_author(self):
        decision = self.create_and_return_example_decision_with_feedback()

        feedback = decision.feedback_set.all()[0]
        self.assertEqual(feedback.author, self.betty)
        # edit feedback
        self.login(self.betty)
        form = FeedbackForm(instance=feedback)
        form.fields['description'] = "New Updated description."
        form.fields['rating'] = 4
        form.fields['resolved'] = False
        # Empty the test outbox
        mail.outbox = []
        response = self.client.post(reverse('publicweb_feedback_update',
            args=[feedback.id]), form.fields)
        self.assertEqual(302, response.status_code)
        self.assertEqual(0, len(mail.outbox))



