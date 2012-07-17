#Test commands that have been added to manage.py
import smtplib
import poplib
import email
import settings
import livesettings
from django.core import management
from publicweb.tests.decision_test_case import OpenConsentTestCase
from publicweb.tests.dummy_poplib import POP3
from publicweb.tests import dummy_poplib
from publicweb.models import Decision, Feedback
from django.core.management.base import CommandError

class CommandTest(OpenConsentTestCase):

    poplib.POP3 = dummy_poplib.POP3
    poplib.POP3_SSL = dummy_poplib.POP3_SSL

    def test_process_email_new_proposal(self):
        #Tests that process_email picks up mails from mailbox
        #and creates objects in the db
        poplib.POP3.mailbox = ([''],['From: Adam <adam@econsensus.com>','To: Admin <admin@econsensus.com>','Subject: Proposal gleda raspored','','Mnogi programi za stolno izdavatvo',''],[''])
        try:
            management.call_command('process_email')
        except:
            self.fail("Exception was raised when processing legitimate email.")
        try:
            decision = Decision.objects.get(description="Mnogi programi za stolno izdavatvo")
        except:
            self.fail("Email failed to appear in database as a decision.")
        self.assertEqual(decision.status, Decision.PROPOSAL_STATUS)
        
    def test_process_email_basic_feedback(self):
        #Tests that if # tag is in the header, but no feedback type is
        #identified then the payload becomes comment feedback
        parent = Decision(status=Decision.PROPOSAL_STATUS)
        parent.save()
        poplib.POP3.mailbox = ([''],['From: Adam <adam@econsensus.com>','To: Admin <admin@econsensus.com>','Subject: gleda raspored #%s' % parent.id,'','Mnogi programi za stolno izdavatvo',''],[''])
        try:
            management.call_command('process_email')
        except:
            self.fail("Exception was raised when processing legitimate email.")
        try:
            feedback = Feedback.objects.get(description="Mnogi programi za stolno izdavatvo")
        except:
            self.fail("Email failed to appear in database as feedback.")
        self.assertEqual(feedback.rating, Feedback.COMMENT_STATUS)

    def test_process_email_defined_feedback(self):
        #Tests that if a defined feedback type is passed it is transformed
        #into the rating field.
        parent = Decision(status=Decision.PROPOSAL_STATUS)
        parent.save()
        poplib.POP3.mailbox = ([''],['From: Adam <adam@econsensus.com>','To: Admin <admin@econsensus.com>','Subject: gleda raspored #%s' % parent.id,'','Danger: Mnogi programi za stolno izdavatvo',''],[''])
        try:
            management.call_command('process_email')
        except:
            self.fail("Exception was raised when processing legitimate email.")
        try:
            feedback = Feedback.objects.get(description="Mnogi programi za stolno izdavatvo")
        except:
            self.fail("Email failed to appear in database as feedback.")
        self.assertEqual(feedback.rating, Feedback.DANGER_STATUS)

    def test_process_email_unrecognised_feedback(self):
        #Tests that if the user mistypes the feedback type it is ignored
        #and the feedback defaults to comment
        parent = Decision(status=Decision.PROPOSAL_STATUS)
        parent.save()
        poplib.POP3.mailbox = ([''],['From: Adam <adam@econsensus.com>','To: Admin <admin@econsensus.com>','Subject: gleda raspored #%s' % parent.id,'','Dager: Mnogi programi za stolno izdavatvo',''],[''])
        try:
            management.call_command('process_email')
        except:
            self.fail("Exception was raised when processing legitimate email.")
        try:
            feedback = Feedback.objects.get(description="Mnogi programi za stolno izdavatvo")
        except:
            self.fail("Email failed to appear in database as feedback.")
        self.assertEqual(feedback.rating, Feedback.COMMENT_STATUS)

    def test_process_email_bad_content(self):
        #Test that an unknown email address is rejected.
        poplib.POP3.mailbox = ([''],['From: Adam <youdontknowme@econsensus.com>','To: Admin <admin@econsensus.com>','Subject: gleda raspored','','Mnogi programi za stolno izdavatvo',''],[''])
        self.assertFalse(Decision.objects.count())
        
        #Test that a corrupt from field is rejected.
        poplib.POP3.mailbox = ([''],['From: Donald <spam>','To: Admin <admin@econsensus.com>','Subject: gleda raspored','','Mnogi programi za stolno izdavatvo',''],[''])
        self.assertFalse(Decision.objects.count())
