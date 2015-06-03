from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from organizations.views import OrganizationDetail
from guardian.shortcuts import assign_perm

from publicweb.views import DecisionDetail, DecisionList
from publicweb.models import Decision, Feedback
from publicweb.forms import DecisionForm
from publicweb.tests.open_consent_test_case import EconsensusFixtureTestCase

# HTML tests test the html code, for example the content of
# dynamic pages based on POST data
class HtmlTest(EconsensusFixtureTestCase):

    def test_add_decision(self):
        """
        Test error conditions for the add decision page.
        """
        path = reverse('publicweb_decision_create', args=[self.bettysorg.slug, Decision.PROPOSAL_STATUS])
        # Test that the decision add view returns an empty form
        site_form = self.client.get(path).context['form']
        code_form = DecisionForm()
        self.assertEqual(type(site_form).__name__, type(code_form).__name__, "Unexpected form!")

        path = reverse('publicweb_decision_create', args=[self.bettysorg.slug, Decision.DECISION_STATUS])
        # Test that the decision add view returns an empty form
        site_form = self.client.get(path).context['form']
        code_form = DecisionForm()
        self.assertEqual(type(site_form).__name__, type(code_form).__name__, "Unexpected form!")

        path = reverse('publicweb_decision_create', args=[self.bettysorg.slug, Decision.ARCHIVED_STATUS])
        # Test that the decision add view returns an empty form
        site_form = self.client.get(path).context['form']
        code_form = DecisionForm()
        self.assertEqual(type(site_form).__name__, type(code_form).__name__, "Unexpected form!")

    # test that the detail view of a decision includes the
    # urlize filter, converting text urls to anchors.
    def test_urlize(self):
        decision = self.make_decision(description="text www.google.com text")
        path = reverse('publicweb_decision_detail', args=[decision.id])
        response = self.client.get(path)
        self.assertContains(response, '<a href="http://www.google.com" rel="nofollow">www.google.com</a>', 1,
                            msg_prefix="Failed to urlize text")

    def test_decision_linebreaks(self):
        decision = self.make_decision(description="text\ntext")
        path = reverse('publicweb_decision_detail', args=[decision.id])
        response = self.client.get(path)
        self.assertContains(response, 'text<br />text', 1,
                            msg_prefix="Failed to line break text")

    def test_feedback_linebreaks(self):
        decision = self.make_decision(description="Lorem")
        feedback = Feedback(description="text\ntext")
        feedback.decision = decision
        feedback.author = self.user
        feedback.save()
        path = reverse('publicweb_feedback_detail', args=[feedback.id])
        response = self.client.get(path)
        self.assertContains(response, 'text<br />text', 1,
                            msg_prefix="Failed to line break text")

    def test_comment_linebreaks(self):
        decision = self.make_decision()
        feedback = self.make_feedback(decision=decision, author=self.user)
        self.make_comment(comment="comment\ntext",
                          object_pk=feedback.id,
                          content_type=ContentType.objects.get_for_model(Feedback)
                          )

        path = reverse('publicweb_feedback_detail', args=[feedback.id])
        response = self.client.get(path)
        self.assertContains(response, 'comment<br />text', 1,
                            msg_prefix="Failed to line break text")

    def test_organization_name_in_header(self):
        path = reverse('publicweb_item_list', args=[self.bettysorg.slug, Decision.PROPOSAL_STATUS])
        response = self.client.get(path)
        self.assertContains(response, self.bettysorg.name)

    def test_author_only_set_once(self):
        path = reverse('publicweb_decision_create', args=[self.bettysorg.slug, Decision.PROPOSAL_STATUS])
        post_dict = {'status': Decision.PROPOSAL_STATUS,
                     'description': 'Lorem Ipsum'}
        response = self.client.post(path, post_dict)
        self.assertRedirects(response, reverse('publicweb_item_list', args=[self.bettysorg.slug, 'proposal']))
        decision = Decision.objects.get(description='Lorem Ipsum')
        self.assertEqual(decision.author, self.user)
        self.user = self.login('charlie')
        # allow charlie to edit
        assign_perm('edit_decisions_feedback', self.user, self.bettysorg)
        path = reverse('publicweb_decision_update', args=[decision.id])
        post_dict = {'status': Decision.PROPOSAL_STATUS,
                     'description': 'ullamcorper nunc'}
        response = self.client.post(path, post_dict)
        self.assertRedirects(response, reverse('publicweb_item_list', args=[self.bettysorg.slug, 'proposal']))
        decision = Decision.objects.get(description='ullamcorper nunc')
        self.assertNotEqual(decision.author, self.user)

    def test_meeting_people_shown(self):
        test_string = 'vitae aliquet tellus'
        path = reverse('publicweb_decision_create', args=[self.bettysorg.slug, Decision.DECISION_STATUS])
        response = self.client.get(path)
        self.assertContains(response, 'meeting_people')
        post_dict = {'description': 'Quisque sapien justo',
                     'meeting_people': test_string,
                     'status': Decision.DECISION_STATUS}
        response = self.client.post(path, post_dict)
        self.assertRedirects(response, reverse('publicweb_item_list', args=[self.bettysorg.slug, post_dict['status']]))
        decision = Decision.objects.get(meeting_people=test_string)
        path = reverse('publicweb_item_detail', args=[decision.id])
        response = self.client.get(path)
        self.assertContains(response, test_string)

    def test_meeting_people_not_shown_for_proposal(self):
        test_string = 'vitae aliquet tellus'
        path = reverse('publicweb_decision_create', args=[self.bettysorg.slug, Decision.DECISION_STATUS])
        post_dict = {'description': 'Quisque sapien justo',
                     'meeting_people': test_string,
                     'status': Decision.PROPOSAL_STATUS}
        response = self.client.post(path, post_dict)
        self.assertRedirects(response, reverse('publicweb_item_list', args=[self.bettysorg.slug, post_dict['status']]))
        proposal = Decision.objects.get(meeting_people=test_string)
        path = reverse('publicweb_item_detail', args=[proposal.id])
        response = self.client.get(path)
        self.assertNotContains(response, test_string)
        
    def test_h2_header_on_form_matches_selected_status(self):
        path = reverse('publicweb_decision_create', args=[self.bettysorg.slug, Decision.PROPOSAL_STATUS])
        response = self.client.get(path)
        self.assertContains(response, 'Proposal')
        path = reverse('publicweb_decision_create', args=[self.bettysorg.slug, Decision.DECISION_STATUS])
        response = self.client.get(path)
        self.assertContains(response, 'Decision')

    def test_site_contains_version_number(self):
        path = reverse('publicweb_root')
        response = self.client.get(path, follow=True)
        self.assertContains(response, '(v0.5.')

    def test_editor_shown(self):
        decision = self.create_decision_through_browser()
        self.login('charlie')
        # allow charlie to edit
        assign_perm('edit_decisions_feedback', self.user, self.bettysorg)

        decision = self.update_decision_through_browser(decision.id)
        path = reverse('publicweb_decision_detail', args=[decision.id])
        response = self.client.get(path, follow=True)
        self.assertContains(response, 'Last edited by')
        self.assertContains(response, 'charlie')

    def test_organization_shown_in_header(self):
        request = self.factory.request()
        request.user = self.betty
        kwargs = {'organization_pk':self.bettysorg.id}
        response = OrganizationDetail(request=request, kwargs=kwargs).get(request, **kwargs)
        rendered_response = response.render()
        self.assertRegexpMatches(rendered_response.content, "<h1>[\s\S]*%s[\s\S]*</h1>" % self.bettysorg)

    def test_cannot_view_decisions_when_not_member(self):

        request = self.factory.request()
        request.user = self.betty
        request.session = self.client.session
        decision = self.make_decision()
        kwargs = {'org_slug' : decision.organization.slug,
                  'status': decision.status}
        response = DecisionList(template_name='decision_list.html').dispatch(request, **kwargs)
        self.assertContains(response, decision.description)

        kwargs = {'pk' : decision.pk}
        response = DecisionDetail(template_name='item_detail.html').dispatch(request, **kwargs)
        self.assertContains(response, decision.description)

        members = [x.username for x in decision.organization.users.all()]
        non_members = User.objects.exclude(username__in=members).exclude(username='AnonymousUser')
        self.assertTrue(non_members)

        self.login(non_members[0].username)
        request.user = self.user
        kwargs = {'org_slug' : decision.organization.slug,
                  'status': decision.status}
        response = DecisionList(template_name='decision_list.html').dispatch(request, **kwargs)
        self.assertNotContains(response, decision.description)

        kwargs = { 'pk' : decision.pk }
        response = DecisionDetail(template_name='item_detail.html').dispatch(request, **kwargs)
        self.assertNotContains(response, decision.description)
