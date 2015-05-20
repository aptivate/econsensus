from django.core.exceptions import ValidationError
from django.utils import timezone
from django.test import TestCase

from notification import models as notification

from publicweb.models import Decision, Feedback
from publicweb.tests.decision_test_case import DecisionTestCase
from publicweb.tests.factories import DecisionFactory, \
                                        FeedbackFactory, \
                                        UserFactory, \
                                        CommentFactory
from publicweb.tests.open_consent_test_case import EconsensusFixtureTestCase

import datetime
from mock import patch, MagicMock
from signals.management import DECISION_CHANGE

# Ensure value of "now" always increases by amount sufficient
# to show up as a change, even if db resolution for datetime
# is one second.
def now_iter(start):
    t = start
    while True:
        t += datetime.timedelta(hours=1)
        yield t

magic_mock = MagicMock(wraps=timezone.now, side_effect=now_iter(timezone.now()))
@patch("django.utils.timezone.now", new=magic_mock)
class DecisionLastModifiedTest(EconsensusFixtureTestCase):
    """
    Tests updating of 'last_modified' date on Decision.
    """
    def setUp(self):
        self.user = UserFactory()
        self.decision = DecisionFactory()

    def last_modified(self):
        """
        Gets the last modified date of the test decision.
        """
        return Decision.objects.get(id=self.decision.id).last_modified

    def test_edit_decision_editor(self):
        orig_last_modified = self.last_modified()
        self.decision.editor = UserFactory()
        self.decision.save()
        self.assertEquals(orig_last_modified, self.last_modified())

    def test_edit_decision_description(self):
        orig_last_modified = self.last_modified()
        self.decision.description += "x"
        self.decision.save()
        self.assertTrue(orig_last_modified < self.last_modified())

    def test_add_feedback_triggers_update(self):
        orig_last_modified = self.last_modified()
        FeedbackFactory(decision=self.decision, author=self.user)
        self.assertTrue(orig_last_modified < self.last_modified())

    def test_add_comment_triggers_update(self):
        feedback = FeedbackFactory(decision=self.decision, author=self.user)
        orig_last_modified = self.last_modified()
        comment = CommentFactory(content_object=feedback, user=self.user)
        self.send_comment_posted_signal(comment)
        self.assertTrue(orig_last_modified < self.last_modified())

    def test_add_watcher_triggers_no_update(self):
        orig_last_modified = self.last_modified()
        notification.observe(self.decision, UserFactory(), DECISION_CHANGE)
        self.decision.save()
        self.assertTrue(orig_last_modified == self.last_modified())


class ModelTest(TestCase):
    def test_get_author_name(self):
        feedback = Feedback(author=None)
        self.assertEqual(feedback.get_author_name(), "An Anonymous Contributor")

        user = UserFactory()
        feedback = FeedbackFactory(author=user)
        self.assertEqual(feedback.get_author_name(), user.username)


class ModelTestSlow(DecisionTestCase):

# Generic test functions:
    def model_has_attribute(self, model, attr):
        self.assertTrue(hasattr(model, attr),
                          "Model %s does not have attribute %s" % (model.__class__, attr))

    def instance_attribute_has_value(self, instance, attr, value):
        target = getattr(instance, attr)
        if callable(target):
            result = target()
        else:
            result = target

        self.assertEqual(value, result,
                          "Attribute %s does not have expected value %s" % (attr, value))

    def instance_validates(self, instance):
        try:
            instance.full_clean()
        except ValidationError, e:
            self.fail("'%s' model instance did not validate: %s" % (instance, e.message_dict))

    def get_column(self, matrix, i):
        return [row[i] for row in matrix]

# The real work:
    def test_decision_has_expected_fields(self):
        decision = self.make_decision()
        self.model_has_attribute(decision, "feedbackcount")
        self.model_has_attribute(decision, "archived_date")
        self.model_has_attribute(decision, "editor")
        self.model_has_attribute(decision, "last_modified")
        self.model_has_attribute(decision, "organization")

    def test_feedback_can_have_empty_description(self):
        decision = self.make_decision()
        feedback = Feedback(rating=Feedback.CONSENT_STATUS, decision=decision)
        self.instance_validates(feedback)

    def test_model_feedbackcount_changes(self):
        decision = self.make_decision()
        self.instance_attribute_has_value(decision, "feedbackcount", 0)
        feedback = Feedback(description="Feedback test data", decision=decision, author=self.user)
        feedback.save()
        self.instance_attribute_has_value(decision, "feedbackcount", 1)

    def test_feedback_rating_has_values(self):
        expected = ('question', 'danger', 'concerns', 'consent', 'comment')
        names = self.get_column(Feedback.RATING_CHOICES, 1)
        actual = []
        for name in names:
            actual.append(unicode(name))

        self.assertEqual(expected, tuple(actual), "Unexpected feedback rating values!")

    def test_feedback_has_author(self):
        decision = self.make_decision()
        feedback = Feedback(description="Feedback test data", decision=decision)
        self.model_has_attribute(feedback, "author")

    def test_decision_has_meeting_people(self):
        decision = self.make_decision()
        self.model_has_attribute(decision, "meeting_people")

    def test_save_when_no_author(self):
        decision = self.make_decision()
        decision.author = None
        decision.description = "A change."
        try:
            decision.save()
        except:
            self.fail("Failed to save object.")

    def test_feedback_statistics(self):
        decision = self.make_decision()
        self.model_has_attribute(decision, "get_feedback_statistics")
        statistics = decision.get_feedback_statistics()
        self.assertTrue("consent" in statistics)
        self.assertTrue("concerns" in statistics)
        self.assertTrue("danger" in statistics)
        self.assertTrue("question" in statistics)
        self.assertTrue("comment" in statistics)


