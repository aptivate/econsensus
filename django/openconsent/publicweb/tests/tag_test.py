from openconsent.publicweb.tests.decision_test_case import DecisionTestCase
from openconsent.publicweb.models import Decision
from openconsent.publicweb.forms import DecisionForm
from tagging.forms import TagField
from django.forms.widgets import TextInput

#TODO: paths should not be hard coded in test code.

class TagsTest(DecisionTestCase):
    def test_tag_can_be_created(self):
        self.login()
        path = "/add/"

        data = {
                'description': 'A description.',
                'tags':'a_tag',
                'status': Decision.PROPOSAL_STATUS,
                'feedback_set-TOTAL_FORMS': '3',
                'feedback_set-INITIAL_FORMS': '0',
                'feedback_set-MAX_NUM_FORMS': '', 
                'submit': 'Save'
        }
        self.client.post(path, data)
        decision = Decision.objects.get(description='A description.')

        self.assertEqual("a_tag", decision.tags)
    
    def test_form_has_tags(self):
        decision_form = DecisionForm()
        self.assertTrue("tags" in decision_form.fields,
                          "Decision form does not contain tags entry")
        
        self.assertEquals(TagField,
                          type(decision_form.fields["tags"]),
                          "Decision form tags is not a TagField")
        
        self.assertEquals(TextInput,
                          type(decision_form.fields["tags"].widget),
                          "Decision form tags is not a TextInput widget")
        
    def test_tags_field_appears_on_page(self): 
        self.login()
        path = "/add/"
        response = self.client.get(path)
        self.assertContains(response, "input id=\"id_tags\"")
    
    def test_page_contains_tags_field_help_text_appears_on_page(self): 
        self.login()
        path = "/add/"
        response = self.client.get(path)
        self.assertContains(response, Decision.TAGS_HELP_FIELD_TEXT)
    
    