from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.core import mail
from openconsent.publicweb.emails import OpenConsentEmailMessage

from publicweb.tests.decision_test_case import DecisionTestCase
from openconsent.publicweb.models import Decision

class EmailTest(DecisionTestCase):
    """
    This class is used to test email sending functionality
    of Open Consent
    """
    
    def test_send_locmem_email(self):
        """
        Tests that django can send an email through the locmem backend
        """
        
        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

        msg = EmailMessage('X', 'Y', 'a@b.c', ['x@y.z'])
        msg.send()
        
        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)
        
        self.assertEqual(msg, outbox[0])
                
    def test_new_decision_sends_email(self):
        #set up a memory based backend
        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
        
        #create a few users
        User.objects.create_user("Andy", "andy@example.com", password='password')
        User.objects.create_user("Billy", "billy@example.com", password='password')
        User.objects.create_user("Chris", "chris@example.com", password='password')

        #add a decision
        decision = self.create_and_return_decision()

        outbox = getattr(mail, 'outbox')
        self.assertTrue(outbox)

        mymail = OpenConsentEmailMessage('new', decision, old_object=None)

        self.assertEqual(mymail, outbox[0])

    def test_emails_dont_contain_escaped_characters(self):
        """
        We want to verify that the emails sent out do not contain
        confusing text like '&amp' instead of '&' or ''&lt'
        instead of '<'
        
        All plaintext emails should be marked 'safe' in the Django template.
        """
        decision = Decision(short_name='&', status=0, description='&')
        decision.save()

        mymail = OpenConsentEmailMessage('new', decision)
        
        self.assertNotIn('&amp', mymail.subject)
        self.assertNotIn('&amp', mymail.body)

        mymail = OpenConsentEmailMessage('status_change', decision, old_object=decision)
        
        self.assertNotIn('&amp', mymail.subject)
        self.assertNotIn('&amp', mymail.body)
        
        mymail = OpenConsentEmailMessage('content_change', decision)
        
        self.assertNotIn('&amp', mymail.subject)
        self.assertNotIn('&amp', mymail.body)
        
