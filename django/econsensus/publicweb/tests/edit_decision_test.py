from django.core.urlresolvers import reverse
from decision_test_case import DecisionTestCase
from publicweb.forms import DecisionForm
from mock import patch
from django.dispatch.dispatcher import Signal
from django.db.models import signals
from publicweb.models import Decision, decision_signal_handler

# TODO: This class is a bit stumpy... merge with other (web) tests.
class EditDecisionTest(DecisionTestCase):

    def test_edit_description_form_displays_title(self):
        decision = self.create_and_return_decision()
        response = self.load_add_decision_and_return_response(decision.id)
        self.assertContains(response, u"Update Proposal #%s" % decision.id)

    def load_add_decision_and_return_response(self, idd):
        return self.client.get(reverse('publicweb_decision_update', args=[idd]))

    @patch('publicweb.models.ObservationManager.send_notifications')
    def test_email_not_sent_when_watcher_removed(self, notifications):
        dispatch_uid = "publicweb.models.decision_signal_handler"
        Signal.disconnect(signals.post_save, sender=Decision,
                          dispatch_uid=dispatch_uid)
        decision = self.create_and_return_decision()
        data = {
              'description': decision.description,
              'status': decision.status,
              'deadline': decision.deadline,
              'people': decision.people,
              'watch': True
        }
        form = DecisionForm(data, instance=decision)
        form.watch = False
        form.is_valid()
        form.save()
        Signal.connect(
            signals.post_save,
            sender=Decision,
            receiver=decision_signal_handler,
            dispatch_uid=dispatch_uid
        )
        self.assertFalse(notifications.called)
