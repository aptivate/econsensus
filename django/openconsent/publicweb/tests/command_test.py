# pylint: disable=W0703
#         W0703 - Too general exception
#Test commands that have been added to manage.py
import poplib
from django.core import management, mail
from publicweb.tests.decision_test_case import OpenConsentTestCase
from publicweb.tests import dummy_poplib
from publicweb.models import Decision, Feedback
from email.mime.text import MIMEText

class CommandTest(OpenConsentTestCase):

    poplib.POP3 = dummy_poplib.POP3
    poplib.POP3_SSL = dummy_poplib.POP3_SSL

    def test_process_email_new_proposal(self):
        #Tests that process_email picks up mails from mailbox
        #and creates objects in the db
        poplib.POP3.mailbox = ([''], [str('From: %s <%s>' % (self.betty, self.betty.email)),
                                      str('To: %s <%s@econsensus.com>' % (self.bettysorg.name, self.bettysorg.slug)),
                                      'Subject: Proposal gleda raspored',
                                      '',
                                      'Mnogi programi za stolno izdavatvo', ''], [''])

        try:
            management.call_command('process_email')
        except:
            self.fail("Exception was raised when processing legitimate email.")
        try:
            decision = Decision.objects.get(description__contains="Mnogi programi za stolno izdavatvo")
        except:
            self.fail("Email failed to appear in database as a decision.")
        self.assertEqual(decision.status, Decision.PROPOSAL_STATUS)
        
    def test_process_email_basic_feedback(self):
        #Tests that if # tag is in the header, but no feedback type is
        #identified then the payload becomes comment feedback
        parent = self.make_decision()
        poplib.POP3.mailbox = ([''], [str('From: %s <%s>' % (self.betty, self.betty.email)),
                                      str('To: %s <%s@econsensus.com>' % (self.bettysorg.name, self.bettysorg.slug)),
                                      'Subject: gleda raspored #%s' % parent.id,
                                      '',
                                      'Mnogi programi za stolno izdavatvo', ''], [''])
        try:
            management.call_command('process_email')
        except:
            self.fail("Exception was raised when processing legitimate email.")
        try:
            feedback = Feedback.objects.get(description__contains="Mnogi programi za stolno izdavatvo")
        except:
            self.fail("Email failed to appear in database as feedback.")
        self.assertEqual(feedback.rating, Feedback.COMMENT_STATUS)

    def test_process_email_defined_feedback(self):
        #Tests that if a defined feedback type is passed it is transformed
        #into the rating field.
        parent = self.make_decision()
        poplib.POP3.mailbox = ([''], [str('From: %s <%s>' % (self.betty, self.betty.email)),
                                      str('To: %s <%s@econsensus.com>' % (self.bettysorg.name, self.bettysorg.slug)),
                                      'Subject: gleda raspored #%s' % parent.id,
                                      '',
                                      'Danger: Mnogi programi za stolno izdavatvo', ''], [''])
        try:
            management.call_command('process_email')
        except:
            self.fail("Exception was raised when processing legitimate email.")
        try:
            feedback = Feedback.objects.get(description__contains="Mnogi programi za stolno izdavatvo")
        except:
            self.fail("Email failed to appear in database as feedback.")
        self.assertEqual(feedback.rating, Feedback.DANGER_STATUS)

    def test_process_email_unrecognised_feedback(self):
        #Tests that if the user mistypes the feedback type it is ignored
        #and the feedback defaults to comment
        parent = self.make_decision()
        poplib.POP3.mailbox = ([''], [str('From: %s <%s>' % (self.betty, self.betty.email)),
                                      str('To: %s <%s@econsensus.com>' % (self.bettysorg.name, self.bettysorg.slug)),
                                      'Subject: gleda raspored #%s' % parent.id,
                                      '',
                                      'Dager: Mnogi programi za stolno izdavatvo', ''], [''])
        try:
            management.call_command('process_email')
        except:
            self.fail("Exception was raised when processing legitimate email.")
        try:
            feedback = Feedback.objects.get(description__contains="Mnogi programi za stolno izdavatvo")
        except:
            self.fail("Email failed to appear in database as feedback.")
        self.assertEqual(feedback.rating, Feedback.COMMENT_STATUS)

    def test_process_email_bad_content(self):
        initial_count = Decision.objects.count()
        #Test that an unknown email address is rejected.
        poplib.POP3.mailbox = ([''], ['From: Secret <youdont@knowme.com>',
                                      str('To: %s <%s@econsensus.com>' % (self.bettysorg.name, self.bettysorg.slug)),
                                      'Subject: gleda raspored',
                                      '',
                                      'Mnogi programi za stolno izdavatvo', ''], [''])
        self.assertFalse(Decision.objects.count() - initial_count)
        
        #Test that a corrupt from field is rejected.
        poplib.POP3.mailbox = ([''], ['From: Donald <spam>',
                                      str('To: %s <%s@econsensus.com>' % (self.bettysorg.name, self.bettysorg.slug)),
                                      'Subject: gleda raspored',
                                      '',
                                      'Mnogi programi za stolno izdavatvo', ''], [''])
        self.assertFalse(Decision.objects.count() - initial_count)

    def test_email_sent_out_on_email_decision(self):
        poplib.POP3.mailbox = ([''], [str('From: %s <%s>' % (self.betty, self.betty.email)),
                                      str('To: self.bettysorg.name <%s@econsensus.com>' % self.bettysorg.slug),
                                      'Subject: Proposal gleda raspored',
                                      '',
                                      'Mnogi programi za stolno izdavatvo', ''], [''])
        try:
            management.call_command('process_email')
        except Exception, e:
            self.fail("Exception: %s" % e)
        
        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)

    def test_email_replies_are_chevron_stripped(self):
        """
        Replies should have any quotes, marked with '>' removed.
        """
        payload = """
        Unquoted text.
        >
        >Some quoted text.
        >
        """
        msg = MIMEText(payload)
        msg['Subject'] = 'Proposal gleda raspored'
        
        msg['From'] = self.betty.email
        msg['To'] = '%s@econsensus.com>' % self.bettysorg.slug
     
        poplib.POP3.mailbox = ([''], [msg.as_string()], [''])
        try:
            management.call_command('process_email')
        except Exception, e:
            self.fail("Exception: %s" % e)
        
        try:
            decision = Decision.objects.get(description__contains="Unquoted text.")
        except:
            self.fail("Email failed to appear in database as a decision.")
        self.assertNotIn("Some quoted text.", decision.description)
        self.assertIn("Unquoted text.", decision.description)
        
    def test_email_replies_are_quote_header_stripped(self):
        """
        Replies should have the 'header' of a quote removed.
        Ie 'On Thursday Tom wrote:'
        """
        payload = """
        Proposal XYZ
        On 24/07/12 18:14, Mark Skipper wrote:
        >
        >Some quoted text.
        >
        """
        msg = MIMEText(payload)
        msg['Subject'] = 'Proposal gleda raspored'
        msg['From'] = self.betty.email
        msg['To'] = '%s@econsensus.com>' % self.bettysorg.slug
        poplib.POP3.mailbox = ([''], [msg.as_string()], [''])
        try:
            management.call_command('process_email')
        except Exception, e:
            self.fail("Exception: %s" % e)
        
        try:
            decision = Decision.objects.get(description__contains="Proposal XYZ")
        except:
            self.fail("Email failed to appear in database as a decision.")
        self.assertNotIn("On 24/07/12 18:14, Mark Skipper wrote:", decision.description)
        self.assertIn("Proposal XYZ", decision.description)
           