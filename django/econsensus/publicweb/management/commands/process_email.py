#management command to update the site with any mail
import poplib
import re
import logging

from email import message_from_string
from django.core.management.base import BaseCommand
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from livesettings import config_value
from publicweb.models import Decision, Feedback
from organizations.models import Organization
from django.conf import settings

def is_autoreply(mail):
    return 'Precedence' in mail and (mail['Precedence'] == "bulk" or 
         mail['Precedence'] == "auto_reply")

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
        except poplib.error_proto, e:
            logger.error(e)
            raise
        except Exception as e:
            logger.error(e)
            raise
        
        num_msgs = mailbox.stat()[0]
        all_msgs = range(1, num_msgs + 1)
        if all_msgs:
            self._print_if_verbose(verbosity, "Processing contents of mailbox.")  
            for i in all_msgs:
                msg = "\n".join(mailbox.retr(i)[1])
                mail = message_from_string(msg) 

                if is_autoreply(mail):
                    log_auto_replies = getattr(settings, 'LOG_AUTO_REPLIES', 
                      False)
                    if log_auto_replies:
                        logger.info(msg)
                    continue
                
                try:
                    self._process_email(mail, verbosity)
                except Exception as e:
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
        logger = logging.getLogger('econsensus')

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
        
        if not msg_string:
            logger.error("[EMAIL REJECTED] From '%s' Reason: Email payload empty" % mail['From'])
            return
        
        #Must match email 'from' address to user
        from_match = re.search('([\w\-\.]+@\w[\w\-]+\.+[\w\-]+)', mail['From'])
        if from_match:
            self._print_if_verbose(verbosity, "Found email 'from' '%s'" % from_match.group(1))
            try:
                user = User.objects.get(email=from_match.group(1))
            except ObjectDoesNotExist:
                logger.error("[EMAIL REJECTED] From '%s' Reason: id '%s' does not correspond to any known User" \
                             % (mail['From'], subject_match.group(1)))
                return
            except MultipleObjectsReturned:
                logger.error("[EMAIL REJECTED] From '%s' Reason: Query returned several Users for id '%s'" \
                             % (mail['From'], subject_match.group(1)))
                return
            self._print_if_verbose(verbosity, "Matched email to user '%s'" % user)
        else:
            logger.error("[EMAIL REJECTED] From '%s' Reason: Unrecognised email address format" % mail['From'])
            return
        
        #Must match email 'to' address to organization
        org_match = re.search('([\w\-\.]+)@\w[\w\-]+\.+[\w\-]+', mail['To'])
        if org_match:
            self._print_if_verbose(verbosity, "Found email 'to' '%s'" % org_match.group(1))
            try:
                organization = Organization.objects.get(slug=org_match.group(1))
            except ObjectDoesNotExist:
                logger.error("[EMAIL REJECTED] From '%s' Reason: id '%s' does not correspond to any known Organization" \
                             % (mail['From'], subject_match.group(1)))
                return
            except MultipleObjectsReturned:
                logger.error("[EMAIL REJECTED] From '%s' Reason: Query returned several Organizations for id '%s'" \
                             % (mail['From'], subject_match.group(1)))
                return
            self._print_if_verbose(verbosity, "Matched email to organization '%s'" % organization.name)
        else:
            logger.error("[EMAIL REJECTED] From '%s' Reason: Couldn't pull Organization from '%s'" % (mail['From'], mail['To']))
            return

        #User must be a member of the Organization
        if organization not in Organization.active.get_for_user(user):
            self._print_if_verbose(verbosity, "User %s is not a member of Organization %s" % (user.username, organization.name))
            logger.error("[EMAIL REJECTED] From '%s' Reason: User '%s' is not a member of Organization '%s'" \
                         % (mail['From'], user.username, organization.name))
            return

        #Look for feedback types in the message body
        rating = Feedback.COMMENT_STATUS                    
        description = msg_string                        
        parse_feedback = re.match('(\w+)\s*:\s*([\s\S]*)', msg_string, re.IGNORECASE)
        if parse_feedback:
            description = parse_feedback.group(2)
            rating_match = re.match('question|danger|concerns|consent|comment', parse_feedback.group(1), re.IGNORECASE)
            if rating_match:
                self._print_if_verbose(verbosity, "Found feedback rating '%s'" % rating_match.group())
                rating = dict(Feedback.RATING_CHOICES).values().index(rating_match.group().lower())

        # Determine whether email is in reply to a notification
        subject_match = re.search('\[EC#(\d+)(?:\\\\(\d+)(?:\\\\(\d+))?)?\]', mail['Subject'])
        if subject_match:
            #Check that the user has the right to comment against the decision.
            if subject_match.group(1):
                self._print_if_verbose(verbosity, "Found decision id '%s' in Subject" % subject_match.group(1))
                try:
                    decision = Decision.objects.get(pk=subject_match.group(1))
                except ObjectDoesNotExist:
                    logger.error("[EMAIL REJECTED] From '%s' Reason: id '%s' does not correspond to any known Decision" \
                                 % (mail['From'], subject_match.group(1)))
                    return
                except MultipleObjectsReturned:
                    logger.error("[EMAIL REJECTED] From '%s' Reason: Query returned several Decisions for id '%s'" \
                                 % (mail['From'], subject_match.group(1)))
                    return
                if user not in decision.organization.users.all():
                    logger.error("[EMAIL REJECTED] From '%s' Reason: User cannot reply to decision #%s because they are not a member of that organization." \
                                 % (mail['From'], subject_match.group(1)))
                    return
                    
            #process comment or feedback against feedback
            if subject_match.group(2):
                self._print_if_verbose(verbosity, "Found feedback id '%s' in Subject" % subject_match.group(2))
                try:
                    feedback = Feedback.objects.get(pk=subject_match.group(2))
                except ObjectDoesNotExist:
                    logger.error("[EMAIL REJECTED] From '%s' Reason: id '%s' does not correspond to any known Feedback" \
                                 % (mail['From'], subject_match.group(2)))
                    return
                except MultipleObjectsReturned:
                    logger.error("[EMAIL REJECTED] From '%s' Reason: Query returned more than one Feedback for id '%s'" \
                                 % (mail['From'], subject_match.group(2)))
                    return
                
                if parse_feedback and rating_match:
                    decision = feedback.decision
                    self._print_if_verbose(verbosity, "Creating feedback with rating '%s' and description '%s'." % (rating, description))
                    feedback = Feedback(author=user, decision=decision, rating=rating, description=description)
                    feedback.save()
                    logger.info("User '%s' added feedback via email to decision #%s" % (user, decision.id))
                    self._print_if_verbose(verbosity, "Found corresponding object '%s'" % decision.excerpt)
                else:
                    comment_text = msg_string                
                    self._print_if_verbose(verbosity, "Creating comment '%s'." % (comment_text))
                    comment = Comment(user=user,
                                     user_name=user.get_full_name(),
                                     user_email=user.email,
                                     comment = comment_text,
                                     content_object=feedback, 
                                     object_pk=feedback.id,
                                     content_type=ContentType.objects.get(app_label="publicweb", model="feedback"),
                                     submit_date = timezone.now(),
                                     site = Site.objects.get_current())
                    comment.save()
                    logger.info("User '%s' added comment via email to feedback #%s" % (user, feedback.id))
                    self._print_if_verbose(verbosity, "Found corresponding object '%s'" % feedback.description)
            
            #process feedback against decision
            elif subject_match.group(1):
                self._print_if_verbose(verbosity, "Creating feedback with rating '%s' and description '%s'." % (rating, description))
                feedback = Feedback(author=user, decision=decision, rating=rating, description=description)
                feedback.save()
                logger.info("User '%s' added feedback via email to decision #%s" % (user, decision.id))
                self._print_if_verbose(verbosity, "Found corresponding object '%s'" % decision.excerpt)
                
            else:
                self._print_if_verbose(verbosity, "No id found in message subject: %s" % mail['Subject'])                
                logger.error("[EMAIL REJECTED] From '%s' Reason: No id present." \
                             % mail['From'])
        # Email was not in reply to a notification so create a new proposal
        else:
            proposal_match = re.search('proposal', mail['Subject'], re.IGNORECASE)
            if proposal_match:
                decision = Decision(author=user, editor=user, status=Decision.PROPOSAL_STATUS, organization=organization, \
                                    description=msg_string)
                decision.save()
                self._print_if_verbose(verbosity, "User '%s' created decision #%s via email" % (user, decision.id))                
                logger.info("User '%s' created decision #%s via email" % (user, decision.id))

            else:
                logger.error("[EMAIL REJECTED] From '%s' Reason: Email was not in reply to a notification and body didn't contain keyword 'proposal'" \
                             % mail['From'])

    def _print_if_verbose(self, verbosity, message):
        if verbosity > 1:
            print message