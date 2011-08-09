from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.core import mail

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
#    def test_add_decision_sends_email(self):
#        #set up a memory based backend
#        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
#
#        #create a few users
#        andy = User.objects.create_user("Andy", "andy@test.com", password='password')
#        billy = User.objects.create_user("Billy", "billy@test.com", password='password')
#        chris = User.objects.create_user("Chris", "chris@test.com", password='password')
#
#        #add a decision
#        self.create_and_return_decision()
#
#        outbox = getattr(mail, 'outbox')
#        self.assertTrue(outbox)
#
#        msg = EmailMessage('X', 'Y', 'a@b.c', ['x@y.z'])
#        
#        self.assertEqual(msg, outbox[0])
#        
#        for object in mail.outbox:
#            print object.subject
#            print object.body
#            print object.from_email
#            print object.to
        
    def test_email_sent_on_edit(self):
        pass


