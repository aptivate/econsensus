from decision_test_case import OpenConsentTestCase
from publicweb.models import Decision, Feedback
from publicweb.forms import DecisionForm
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

#HTML tests test the html code, for example the content of 
#dynamic pages based on POST data
class HtmlTest(OpenConsentTestCase):

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
        
    def test_decision_linebreaks(self):
        decision = Decision(description="text\ntext")
        decision.save()
        path = reverse('publicweb_decision_detail', args=[decision.id])
        response = self.client.get(path)
        self.assertContains(response, 'text<br />text', 1, 
                            msg_prefix="Failed to line break text")
    
    def test_feedback_linebreaks(self):
        decision = Decision(description="Lorem")
        decision.save()
        feedback = Feedback(description="text\ntext")
        feedback.decision = decision
        feedback.save()
        path = reverse('publicweb_feedback_detail', args=[feedback.id])
        response = self.client.get(path)
        self.assertContains(response, 'text<br />text', 1, 
                            msg_prefix="Failed to line break text")
    
    def test_sitename_in_header(self):
        path = reverse('publicweb_item_list', args=[Decision.PROPOSAL_STATUS])
        response = self.client.get(path)
        current_site = Site.objects.get_current()   
        self.assertContains(response, current_site.name)
        
    def test_author_only_set_once(self):
        path = reverse('publicweb_decision_create', args=[Decision.PROPOSAL_STATUS])
        post_dict = {'status': Decision.PROPOSAL_STATUS,
                     'description': 'Lorem Ipsum'}
        response = self.client.post(path, post_dict)
        self.assertRedirects(response,reverse('publicweb_item_list', args=['proposal']))
        decision = Decision.objects.get(description='Lorem Ipsum')
        self.assertEqual(decision.author, self.user)
        self.user = self.login('Barry')
        
        path = reverse('publicweb_decision_update', args=[decision.id])
        post_dict = {'status': Decision.PROPOSAL_STATUS,
                     'description': 'ullamcorper nunc'}
        response = self.client.post(path, post_dict)
        self.assertRedirects(response,reverse('publicweb_item_list', args=['proposal']))
        decision = Decision.objects.get(description='ullamcorper nunc')
        self.assertNotEqual(decision.author, self.user)
    
    def test_feedback_author_shown(self):
        self.user = self.login('Barry')
        decision = Decision(description="Lorem Ipsum")
        decision.save()
        feedback = Feedback(description="Dolor sit")
        feedback.author = self.user
        feedback.decision = decision
        feedback.save()
        
        self.user = self.login('Adam')        
        path = reverse('publicweb_item_detail', args=[decision.id])
        response = self.client.get(path)
        barry = User.objects.get(username='Barry')
        self.assertContains(response, barry.username)
        
    def test_meeting_people_shown(self):
        test_string = 'vitae aliquet tellus'
        path = reverse('publicweb_decision_create', args=[Decision.DECISION_STATUS])
        response = self.client.get(path)
        self.assertContains(response, 'meeting_people')
        post_dict = {'description': 'Quisque sapien justo', 
                     'meeting_people': test_string, 
                     'status': Decision.PROPOSAL_STATUS}
        response = self.client.post(path,post_dict)
        self.assertRedirects(response, reverse('publicweb_item_list', args=[Decision.PROPOSAL_STATUS]))
        decision = Decision.objects.get()
        path = reverse('publicweb_item_detail', args=[decision.id])
        response = self.client.get(path)  
        self.assertContains(response, test_string)
        
    def test_h2_header_on_form_matches_selected_status(self):
        path = reverse('publicweb_decision_create', args=[Decision.PROPOSAL_STATUS])
        response = self.client.get(path)
        self.assertContains(response, 'Proposal')
        path = reverse('publicweb_decision_create', args=[Decision.DECISION_STATUS])
        response = self.client.get(path)
        self.assertContains(response, 'Decision')
        