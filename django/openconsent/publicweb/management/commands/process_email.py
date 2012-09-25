#management command to update the site with any mail
import poplib
import re
import logging
from email import message_from_string
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from livesettings import config_value
from organizations.models import Organization
from publicweb.models import Decision, Feedback, rating_int

class Command(BaseCommand):
    args = ''
    help = 'Checks for emails and posts content to site.'

    def handle(self, *args, **options): # pylint: disable=R0914
        verbosity = int(options.get('verbosity', 1))
        user = config_value('ReceiveMail', 'USERNAME')
        password = config_value('ReceiveMail', 'PASSWORD')
        server = config_value('ReceiveMail', 'SERVER')
        port = config_value('ReceiveMail', 'PORT')
        ssl = config_value('ReceiveMail', 'SSL_ENABLED')
        logger = logging.getLogger('econsensus')

        try:
            if ssl == True: 
                mailbox = poplib.POP3_SSL(server, port)
            else: 
                mailbox = poplib.POP3(server, port)

            mailbox.user(user)
            mailbox.pass_(password)
        except Exception, e:
            logger.error(e)
        
        num_msgs = mailbox.stat()[0]
        all_msgs = range(1, num_msgs + 1)
        if all_msgs:
            self._print_if_verbose(verbosity, "Processing contents of mailbox.")  
            for i in all_msgs:
                msg = mailbox.retr(i)[1]
                mail = message_from_string("\n".join(msg))
                try:
                    self._process_email(mail, verbosity)
                except Exception, e:
                    logger.error(e)
                finally:                    
                    mailbox.dele(i)
        else: self._print_if_verbose(verbosity, "Nothing to do!")  

        mailbox.quit()

    def _strip_string(self, payload, verbosity):
        msg_string = payload.strip('\n')
        msg_string = re.sub('\s*>.*', '', msg_string)
        msg_string = re.sub("On ([a-zA-Z0-9, :/<>@\.\"\[\]]* wrote:.*)", '', msg_string)
        if not msg_string:
            self._print_if_verbose(verbosity, "Email message payload was empty!")
        return msg_string

    def _process_email(self, mail, verbosity): # pylint: disable=R0914
        user = None
        decision = None
        user_found = False
        object_found = False
        org_found = False
        msg_string = ''
        
        #match email 'from' address to user
        from_match = re.search('([\w\-\.]+@\w[\w\-]+\.+[\w\-]+)', mail['From'])
        if from_match:
            self._print_if_verbose(verbosity, "Found email 'from' '%s'" % from_match.group(1))
            try:
                user = User.objects.get(email=from_match.group(1))
                user_found = True
                self._print_if_verbose(verbosity, "Matched email to user '%s'" % user)
            except:
                pass

        #match id to object
        id_match = re.search('#(\d+)', mail['Subject'])        
        if id_match:
            self._print_if_verbose(verbosity, "Found '%s' in Subject" % id_match.group())
            try:
                decision = Decision.objects.get(pk=id_match.group(1))
                object_found = True
                self._print_if_verbose(verbosity, "Found corresponding object '%s'" % decision.excerpt)
            except:
                pass
        
        #match email 'to' address to organization
        to_match = re.search('([\w\-\.]+)@\w[\w\-]+\.+[\w\-]+', mail['To'])
        if to_match:
            self._print_if_verbose(verbosity, "Found email 'to' '%s'" % to_match.group(1))
            try:
                organization = Organization.objects.get(slug=to_match.group(1))
                org_found = True
                self._print_if_verbose(verbosity, "Matched email to organization '%s'" % organization.name)
            except:
                pass
        
        proposal_found = re.search('proposal', mail['Subject'], re.IGNORECASE)

        #handle multipart mails, cycle through mail 
        #until find text type with a full payload.
        if mail.is_multipart():
            for message in mail.get_payload():
                if message.get_content_maintype() == 'text':
                    msg_string = self._strip_string(message.get_payload(), verbosity)
                    if msg_string:
                        break
        else:
            msg_string = self._strip_string(mail.get_payload(), verbosity)       

        if user_found and msg_string:
            if object_found:
                parse_feedback = re.match('(\w+)\s*:\s*(\w+[\s\w]*)', msg_string, re.IGNORECASE)
                if parse_feedback:
                    description = parse_feedback.group(2)
                    rating_match = re.match('question|danger|concerns|consent|comment', parse_feedback.group(1), re.IGNORECASE)
                else:
                    rating_match = None
                    description = msg_string
                    
                if rating_match:
                    self._print_if_verbose(verbosity, "Found feedback rating '%s'" % rating_match.group())
                    rating = rating_int(rating_match.group().lower())
                else:
                    rating = Feedback.COMMENT_STATUS

                self._print_if_verbose(verbosity, "Creating feedback with rating '%s' and description '%s'." % (rating, description))
                feedback = Feedback(author=user, decision=decision, rating=rating, description=description)
                feedback.save()
            elif proposal_found and org_found:
                self._print_if_verbose(verbosity, "No matching object, creating proposal")
                if organization in Organization.active.get_for_user(user):
                    decision = Decision(author=user, editor=user, status=Decision.PROPOSAL_STATUS, organization=organization, description=msg_string)
                    decision.save()
                else:
                    self._print_if_verbose(verbosity, "User %s is not a member of Organization %s" % (user.username, organization.name))
        
    def _print_if_verbose(self, verbosity, message):
        if verbosity > 1:
            print message