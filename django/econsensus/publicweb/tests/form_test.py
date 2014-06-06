from django.core.urlresolvers import reverse

from organizations.models import Organization

from decision_test_case import DecisionTestCase
from publicweb.forms import FeedbackForm, NotificationsForm
from mock import patch
from notification.models import observe
from signals.management import DECISION_CHANGE

#Put any form tests here
class FormTest(DecisionTestCase):
    
    def test_owner_of_new_org_is_admin_and_editor(self):
        """
        Owner of new organization should be the creating user, and they 
        should be both admin and editor.
        """
        new_org_name = new_org_slug = "neworg"
        self.assertEqual(Organization.objects.filter(slug=new_org_slug).count(), 0, "Organization with this slug already exists")
        path = reverse("organization_add")
        response = self.client.post(
            path, 
            {"name": new_org_name, "slug": new_org_slug, "email": self.charlie.email}
        )
        organizations = Organization.objects.filter(slug=new_org_slug)
        self.assertEqual(organizations.count(), 1, "The Organization wasn't created")
        new_organization = organizations[0]
        self.assertTrue(new_organization.is_owner(self.user), "New Organization has wrong owner")
        self.assertTrue(new_organization.owner.organization_user.is_admin, "Owner of new Organization is not admin")
        self.assertTrue(self.user.has_perm('edit_decisions_feedback', new_organization), "Owner of new Organization is not editor")
    
    def test_feedback_form_has_watch_field(self):
        form = FeedbackForm()
        self.assertIn('watch', form.fields)
    
    @patch('publicweb.models.notification.observe')
    def test_change_observers_adds_when_not_watching_and_watch_true(
        self, observe
    ):
        feedback = self.create_and_return_feedback()
        form = NotificationsForm(instance=feedback)
        form.cleaned_data = {'watch': True}
        form.change_observers(feedback.decision, feedback.author)
        self.assertTrue(observe.called)
    
    @patch('notification.models.observe')
    def test_change_observers_doesnt_add_when_watching_and_watch_true(
        self, observe_method
    ):
        feedback = self.create_and_return_feedback()
        observe(feedback.decision, feedback.author, DECISION_CHANGE)
        form = NotificationsForm(instance=feedback)
        form.cleaned_data = {'watch': True}
        form.change_observers(feedback.decision, feedback.author)
        self.assertFalse(observe_method.called)
    
    @patch('notification.models.stop_observing')
    def test_change_observers_doesnt_remove_when_not_watching_and_watch_false(
        self, stop_observe
    ):
        feedback = self.create_and_return_feedback()
        form = NotificationsForm(instance=feedback)
        form.cleaned_data = {'watch': False}
        form.change_observers(feedback.decision, feedback.author)
        self.assertFalse(stop_observe.called)
    
    @patch('notification.models.stop_observing')
    def test_change_observers_removes_when_watching_and_watch_false(
        self, stop_observe
    ):
        feedback = self.create_and_return_feedback()
        observe(feedback.decision, feedback.author, DECISION_CHANGE)
        form = NotificationsForm(instance=feedback)
        form.cleaned_data = {'watch': False}
        form.change_observers(feedback.decision, feedback.author)
        self.assertTrue(stop_observe.called)