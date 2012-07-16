#management command to update the site with any mail
import poplib
import re
import sys
import email

from livesettings import config_value
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from publicweb.models import Decision, Feedback

class Command(BaseCommand):
    args = ''
    help = 'Checks for emails and posts content to site.'

    def handle(self, *args, **options):
        user = config_value('PostByEmail', 'USERNAME')
        password = config_value('PostByEmail', 'PASSWORD')
        server = config_value('PostByEmail', 'SERVER')
        port = config_value('PostByEmail', 'PORT')
        ssl = config_value('PostByEmail', 'SSL_ENABLED')

        try:
            if ssl==True: 
                Mailbox = poplib.POP3_SSL(server, port)
            else: 
                Mailbox = poplib.POP3(server, port)

            Mailbox.user(user)
            Mailbox.pass_(password)
        except:
            raise CommandError("Error accessing email. Check your mail settings.")
        
        (numMsgs, totalSize) = Mailbox.stat()
        for i in range(1, numMsgs + 1):
            (header, msg, octets) = Mailbox.retr(i)
            mail = email.message_from_string("\n".join(msg))
            self._process_email(mail)
            Mailbox.dele(i)
        Mailbox.quit()
        
    def _process_email(self,mail):
        user = None
        decision = None
        user_found = False
        object_found = False
        email_found = re.search('<([\w\-\.]+@\w[\w\-]+\.+[\w\-]+)>', mail['From'])
        if email_found:
            try:
                user = User.objects.get(email=email_found.group(1))
                user_found = True
            except:
                pass
        id_found = re.search('#(\d+)', mail['Subject'])
        proposal_found = re.search('proposal', mail['Subject'], re.IGNORECASE)
        if id_found:
            try:               
                decision = Decision.objects.get(pk=id_found.group(1))
                object_found = True
            except:
                pass

        msg_string = mail.get_payload().strip('\n')
        
        if user_found and msg_string:
            if object_found:
                feedback = Feedback(author=user, decision=decision,rating=Feedback.COMMENT_STATUS, description=msg_string)
                feedback.save()
            elif proposal_found:
                decision = Decision(author=user,status=Decision.PROPOSAL_STATUS, description=msg_string)
                decision.save()
                