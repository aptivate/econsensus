from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.core import mail
from openconsent.publicweb.emails import OpenConsentEmailMessage

from publicweb.tests.decision_test_case import DecisionTestCase

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
                
#Work in Progress...
    def test_add_decision_sends_email(self):
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
        
    def test_email_sent_on_edit(self):
        pass


