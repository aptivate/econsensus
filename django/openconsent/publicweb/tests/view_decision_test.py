from django.core.urlresolvers import reverse
from publicweb.tests.decision_test_case import DecisionTestCase

# TODO: Check that POSTs save correct data and redirects work
class ViewDecisionTest(DecisionTestCase):
    def test_view_decision(self):
        decision = self.create_and_return_decision()
        response = self.client.get(reverse('view_decision', args=[decision.id]))

        self.assertContains(response, u"Edit proposal: <span>%s</span>" % decision.excerpt)
        self.assertContains(response, u'<rect width="9"')

    def test_view_decision_with_feedback(self):
        decision = self.create_and_return_example_decision_with_feedback()
        response = self.client.get(reverse('view_decision', args=[decision.id]))

        self.assertContains(response, u"Edit proposal: <span>%s</span>" % decision.excerpt)
        self.assertContains(response, u'<rect width="9"')
        self.assertContains(response, u'<span class="feedback_all">1</span>')
        self.assertContains(response, u'<ol class="feedback_list">')

    def test_load_decision_snippet(self):
        decision = self.create_and_return_decision()
        response = self.client.get(reverse('view_decision_snippet', args=[decision.id]))

        self.assertContains(response, u'<a href="/view/%s/edit/">Edit</a>' % decision.id)
        self.assertTrue(response.content.strip().startswith('<div id="decision">'))
        self.assertContains(response, u'<rect width="9"')

    def test_load_form_snippet(self):
        form_fields = set(['status', 'review_date', 'description', 'tags', 'budget', 'effective_date', 'csrfmiddlewaretoken', 'decided_date'])
        decision = self.create_and_return_decision()
        response = self.client.get(reverse('inline_edit_decision_form', args=[decision.id]))

        self.assertTrue(response.content.strip().startswith('<form action="#" method="post" class="edit_decision_form">'))

        form_data = self.get_form_values_from_response(response, 1)
        self.assertTrue(form_fields.issubset(set(form_data.keys())))

    def test_load_decision_form(self):
        form_fields = set(['status', 'review_date', 'description', 'tags', 'budget', 'effective_date', 'csrfmiddlewaretoken', 'decided_date'])
        decision = self.create_and_return_decision()
        response = self.client.get(reverse('inline_edit_decision', args=[decision.id]))
        response_content = response.content.strip()

        self.assertFalse(response_content.startswith('<form action="#" method="post" class="edit_decision_form">'))
        self.assertTrue(response_content.startswith('<!DOCTYPE html'))
        self.assertContains(response, u"Edit proposal: <span>%s</span>" % decision.excerpt)

        form_data = self.get_form_values_from_response(response, 2)
        self.assertTrue(form_fields.issubset(set(form_data.keys())))
