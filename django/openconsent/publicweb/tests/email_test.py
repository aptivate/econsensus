from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.core import mail
from publicweb.emails import OpenConsentEmailMessage

from publicweb.tests.decision_test_case import DecisionTestCase
from publicweb.models import Decision

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
        decision = Decision(description='&', status=0)
        decision.save(self.user)

        mymail = OpenConsentEmailMessage('new', decision)
        
        self.assertNotIn('&amp', mymail.subject)
        self.assertNotIn('&amp', mymail.body)

        mymail = OpenConsentEmailMessage('status_change', decision, old_object=decision)
        
        self.assertNotIn('&amp', mymail.subject)
        self.assertNotIn('&amp', mymail.body)
        
        mymail = OpenConsentEmailMessage('content_change', decision)
        
        self.assertNotIn('&amp', mymail.subject)
        self.assertNotIn('&amp', mymail.body)
        
    def test_emails_arent_sent_to_author(self):
        """
        We want to make sure that when a user creates or changes an 
        item they are not sent an email. The email goes to those
        that do not already know the item has changed!
        """
        andy = User.objects.create_user("Andy", "andy@example.com", password='password')
        billy = User.objects.create_user("Billy", "billy@example.com", password='password')
        chris = User.objects.create_user("Chris", "chris@example.com", password='password')
        
        decision = Decision(description='Test', status=0)
        decision.save(andy)
        
        #billy decides he wants to watch...
        decision.watchers = [billy]

        #andy changes the content
        mymail = OpenConsentEmailMessage('content_change', decision)
        
        #only watchers get mail, not the author
        self.assertNotIn(andy.email, mymail.to)
        self.assertIn(billy.email, mymail.to)         
        self.assertNotIn(chris.email, mymail.to)
