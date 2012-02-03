from decision_test_case import DecisionTestCase
from publicweb.models import Decision
from publicweb.forms import DecisionForm
from django.core.urlresolvers import reverse

#HTML tests test the html code, for example the content of 
#dynamic pages based on POST data
class HtmlTest(DecisionTestCase):

    def test_add_decision(self):
        """
        Test error conditions for the add decision page. 
        """
        path = reverse('publicweb_decision_create', args=[Decision.PROPOSAL_STATUS])
        # Test that the decision add view returns an empty form
        site_form = self.client.get(path).context['form']
        code_form = DecisionForm()
        self.assertEqual(type(site_form).__name__, type(code_form).__name__, "Unexpected form!")

        path = reverse('publicweb_decision_create', args=[Decision.DECISION_STATUS])
        # Test that the decision add view returns an empty form
        site_form = self.client.get(path).context['form']
        code_form = DecisionForm()
        self.assertEqual(type(site_form).__name__, type(code_form).__name__, "Unexpected form!")

        path = reverse('publicweb_decision_create', args=[Decision.ARCHIVED_STATUS])
        # Test that the decision add view returns an empty form
        site_form = self.client.get(path).context['form']
        code_form = DecisionForm()
        self.assertEqual(type(site_form).__name__, type(code_form).__name__, "Unexpected form!")

    #test that the detail view of a decision includes the 
    #urlize filter, converting text urls to anchors.
    def test_urlize(self):
        decision = Decision(description="text www.google.com text")
        decision.save()
        path = reverse('publicweb_decision_detail', args=[decision.id])
        response = self.client.get(path)
        self.assertContains(response, '<a href="http://www.google.com" rel="nofollow">www.google.com</a>', 1, 
                            msg_prefix="Failed to urlize text")
        
    def test_linebreaks(self):
        decision = Decision(description="text\ntext")
        decision.save()
        path = reverse('publicweb_decision_detail', args=[decision.id])
        response = self.client.get(path)
        self.assertContains(response, 'text<br />text', 1, 
                            msg_prefix="Failed to line break text")
        