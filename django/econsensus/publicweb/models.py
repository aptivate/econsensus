# pylint: disable=E1102
# config import is unused but required here for livesettings
import config  # pylint: disable=W0611
import re

from notification import models as notification

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.comments.signals import comment_was_posted
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Count
from django.dispatch.dispatcher import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, ugettext_noop

from organizations.models import Organization

# Ideally django-tinymce should be patched
# http://south.aeracode.org/wiki/MyFieldsDontWork
# http://code.google.com/p/django-tinymce/issues/detail?id=80
# TODO: Status codes could possibly be harvested off into its
# own class with accessor methods to return values.

from south.modelsinspector import add_introspection_rules
from tagging.fields import TagField

from managers import DecisionManager
from signals.management import (DECISION_CHANGE, MINOR_CHANGE, DECISION_NEW,
    FEEDBACK_NEW, FEEDBACK_CHANGE, COMMENT_NEW, DECISION_STATUS_CHANGE,
    ACTIONITEM_NEW, ACTIONITEM_CHANGE)


from publicweb.observation_manager import ObservationManager
# The NotificationSettings and OrganizationSettings models were moved to a
# separate file to prevent circular imports. They need to be here or django
# won't detect them.
from publicweb.extra_models import (STANDARD_SENDING_HEADERS,
    NotificationSettings, MINOR_CHANGES_NOTIFICATIONS)  # pylint: disable=W0611
from publicweb.utils import get_excerpt


add_introspection_rules([], ["^tagging\.fields\.TagField"])


class Decision(models.Model):

    TAGS_HELP_FIELD_TEXT = "Enter a list of tags separated by spaces."
    DISCUSSION_STATUS = 'discussion'
    PROPOSAL_STATUS = 'proposal'
    DECISION_STATUS = 'decision'
    ARCHIVED_STATUS = 'archived'

    STATUS_CHOICES = (
                  (DISCUSSION_STATUS, _('discussion')),
                  (PROPOSAL_STATUS, _('proposal')),
                  (DECISION_STATUS, _('decision')),
                  (ARCHIVED_STATUS, _('archived')),
                  )

    DEFAULT_SIZE = 140

    # User entered fields
    description = models.TextField(verbose_name=_('Description'))
    decided_date = models.DateField(null=True, blank=True,
        verbose_name=_('Decided Date'))
    effective_date = models.DateField(null=True, blank=True,
        verbose_name=_('Effective Date'))
    review_date = models.DateField(null=True, blank=True,
        verbose_name=_('Review Date'))
    expiry_date = models.DateField(null=True, blank=True,
        verbose_name=_('Expiry Date'))
    deadline = models.DateField(null=True, blank=True,
        verbose_name=_('Deadline'))
    archived_date = models.DateField(null=True, blank=True,
        verbose_name=_('Archived Date'))
    budget = models.CharField(blank=True, max_length=255,
        verbose_name=_('Budget/Resources'))
    people = models.CharField(max_length=255, null=True, blank=True)
    meeting_people = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(choices=STATUS_CHOICES,
                                 default=PROPOSAL_STATUS,
                                 max_length=10)
    tags = TagField(null=True, blank=True, editable=True,
                    help_text=TAGS_HELP_FIELD_TEXT)
    organization = models.ForeignKey(Organization)
    # admin stuff
    author = models.ForeignKey(User, blank=True, null=True, editable=False, related_name="%(app_label)s_%(class)s_authored")
    editor = models.ForeignKey(User, blank=True, null=True, editable=False, related_name="%(app_label)s_%(class)s_edited")
    last_modified = models.DateTimeField(null=True, auto_now_add=True, verbose_name=_('Last Modified'))
    last_status = models.CharField(choices=STATUS_CHOICES,
                                 default="new",
                                 max_length=10, editable=False)

    watchers = generic.GenericRelation(notification.ObservedItem)

    # Autocompleted fields
    # should use editable=False?
    excerpt = models.CharField(verbose_name=_('Excerpt'), max_length=255, blank=True)
    creation = models.DateField(null=True, auto_now_add=True,
        verbose_name=_('Creation'))

    objects = DecisionManager()

    # Fields that'll trigger last_modified update upon change
    TRIGGER_FIELDS = ('description', 'decided_date', 'effective_date', 'review_date',
              'expiry_date', 'deadline', 'archived_date', 'budget', 'people',
              'meeting_people', 'excerpt', 'creation')

    def __init__(self, *args, **kwargs):
        # Unpersisted flag for suppressing notifications at save time
        self.minor_edit = False

        super(Decision, self).__init__(*args, **kwargs)

    # methods
    def unresolvedfeedback(self):
        answer = _("No")
        linked_feedback = self.feedback_set.all()
        for thisfeedback in linked_feedback:
            if (not thisfeedback.resolved):

                answer = _("Yes")
                break

        return answer

    unresolvedfeedback.short_description = _("Unresolved Feedback")

    def feedbackcount(self):
        return self.feedback_set.all().count()

    feedbackcount.short_description = _("Feedback")

    def _get_excerpt(self):
        return get_excerpt(self.description)

    def __unicode__(self):
        return self.excerpt

    @classmethod
    def get_fields(cls):
        return cls._meta.fields

    @models.permalink
    def get_absolute_url(self):
        return ('publicweb_item_detail', [self.id])

    def get_email(self):
        """
        Generates an email address based on the Decision's organization
        and settings.DEFAULT_FROM_EMAIL
        """
        default_from_email = settings.DEFAULT_FROM_EMAIL
        return re.sub('\w+@', "%s@" % self.organization.slug, default_from_email)

    def get_feedback_statistics(self):
        statistics = dict([(unicode(x), 0) for x in Feedback.rating_names])
        raw_data = self.feedback_set.values('rating').annotate(Count('rating'))
        for x in raw_data:
            key = unicode(Feedback.rating_names[x['rating']])
            statistics[key] = x['rating__count']
        return statistics

    def get_message_id(self):
        """
        Generates a message id that can be used in email headers
        """
        return "<decision-%s@%s>" % (self.id, Site.objects.get_current().domain)

    def _send_change_notifications(self, notification_type):
        headers = {'Message-ID': self.get_message_id()}
        headers.update(STANDARD_SENDING_HEADERS)
        org_users = self.organization.users.all()
        observation_manager = ObservationManager()
        observation_manager.send_notifications(org_users, self, notification_type, {"observed": self}, headers=headers, from_email=self.get_email())

    def _send_minor_change_notifications(self):
        self._send_change_notifications(MINOR_CHANGE)

    def _send_major_change_notifications(self):
        self._send_change_notifications(DECISION_CHANGE)

    def _is_same(self, other):
        for field in self.TRIGGER_FIELDS:
            my_field = getattr(self, field)
            other_field = getattr(other, field)
            if (my_field != other_field
                and not (my_field == u'' and other_field is None)):
                return False
        return True

    def _update_last_modified(self):
        self.last_modified = timezone.now()

    def save(self, *args, **kwargs):
        self.excerpt = self._get_excerpt()
        if self.id:
            prev = self.__class__.objects.get(id=self.id)
            if prev.organization.id != self.organization.id:
                self.watchers.all().delete()

            notification_sent = False
            if self.status != prev.status:
                self._send_change_notifications(DECISION_STATUS_CHANGE)
                self._update_last_modified()
                notification_sent = True

            if not self._is_same(prev) and not notification_sent:
                if not self.minor_edit:
                    self._send_major_change_notifications()
                else:
                    self._send_minor_change_notifications()
                self._update_last_modified()

        super(Decision, self).save(*args, **kwargs)

    def note_external_modification(self):
        """
        Called when some other object is saved (e.g. a comment
        and we want this to be reflected in this decision's
        "last modified" date.
        """
        self._update_last_modified()
        # Go to superclass to avoid sending email notifications
        super(Decision, self).save()


class Feedback(models.Model):

    rating_names = (ugettext_noop('question'),
                    ugettext_noop('danger'),
                    ugettext_noop('concerns'),
                    ugettext_noop('consent'),
                    ugettext_noop('comment'))

    RATING_CHOICES = [(rating_names.index(x), x) for x in rating_names]

    QUESTION_STATUS = rating_names.index('question')
    DANGER_STATUS = rating_names.index('danger')
    CONCERNS_STATUS = rating_names.index('concerns')
    CONSENT_STATUS = rating_names.index('consent')
    COMMENT_STATUS = rating_names.index('comment')

    description = models.TextField(verbose_name=_('Description'), null=True, blank=True)
    author = models.ForeignKey(User, blank=True, null=True, editable=False, related_name="%(app_label)s_%(class)s_related")
    editor = models.ForeignKey(User, blank=True, null=True, editable=False, related_name="%(app_label)s_%(class)s_edited")
    decision = models.ForeignKey('Decision', verbose_name=_('Decision'))
    resolved = models.BooleanField(verbose_name=_('Resolved'))
    rating = models.IntegerField(choices=RATING_CHOICES, default=COMMENT_STATUS)

    watchers = generic.GenericRelation(notification.ObservedItem)
    comments = generic.GenericRelation(Comment, object_id_field='object_pk')

    def __init__(self, *args, **kwargs):
        # Unpersisted flag for suppressing notifications at save time
        self.minor_edit = False

        super(Feedback, self).__init__(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('publicweb_feedback_detail', [self.id])

    @models.permalink
    def get_parent_url(self):
        return ('publicweb_item_detail', [self.decision.id])

    def get_author_name(self):
        if hasattr(self.author, 'username') and self.author.username:
            return self.author.username
        else:
            return "An Anonymous Contributor"

    def get_message_id(self):
        """
        Generates a message id that can be used in email headers
        """
        return "<feedback-%s@%s>" % (self.id, Site.objects.get_current().domain)


def get_action_item_message_id(actionitem):
    """
    Generates a message id that can be used in email headers
    """
    return "<actionitem-%s@%s>" % (actionitem.id, Site.objects.get_current().domain)


def send_decision_notifications(decision, users):
    headers = {'Message-ID' : decision.get_message_id()}
    headers.update(STANDARD_SENDING_HEADERS)
    extra_context = {"observed": decision}
    observation_manager = ObservationManager()
    observation_manager.send_notifications(
                    users, decision, DECISION_NEW, extra_context, headers,
                    from_email=decision.get_email())


# TODO: Test this
def send_comment_notifications(comment, users):
    headers = {'Message-ID' : "comment-%s@%s" % (comment.id, Site.objects.get_current().domain)}
    headers.update(STANDARD_SENDING_HEADERS)
    headers.update({'In-Reply-To' : comment.content_object.get_message_id()})

    comment.content_object.decision.note_external_modification()

    observation_manager = ObservationManager()

    extra_context = dict({"observed": comment})
    observation_manager.send_notifications(users, comment, COMMENT_NEW, extra_context, headers, from_email=comment.content_object.decision.get_email())


def additional_message_required(user, decision, level):
    organization = decision.organization

    result = notification.is_observing(decision, user)

    notification_settings, _ = NotificationSettings.objects.get_or_create(user=user, organization=organization)
    result = not result and notification_settings.notification_level < level

    return result


def change_observers(watch, decision, watcher):
    if watch:
        if not notification.is_observing(decision, watcher):
            notification.observe(decision, watcher, DECISION_CHANGE)
    else:
        if notification.is_observing(decision, watcher):
            notification.stop_observing(decision, watcher)


@receiver(models.signals.post_save, sender=Decision, dispatch_uid="publicweb.models.decision_signal_handler")
def decision_signal_handler(sender, **kwargs):
    """
    All users except the author will get a notification informing them of
    new content.
    All users are made observers of the decision.
    """
    instance = kwargs.get('instance')
    headers = {'Message-ID' : instance.get_message_id()}
    headers.update(STANDARD_SENDING_HEADERS)
    if kwargs.get('created', True):
        active_users = instance.organization.users.filter(is_active=True)
        extra_context = {"observed": instance}
        observation_manager = ObservationManager()
        observation_manager.send_notifications(active_users, instance, DECISION_NEW, extra_context, headers, from_email=instance.get_email())


@receiver(models.signals.post_save, sender=Feedback, dispatch_uid="publicweb.models.feedback_signal_handler")
def feedback_signal_handler(sender, **kwargs):
    """
    All watchers of a decision will get a notification informing them of
    new feedback.
    All watchers become observers of the feedback.
    """
    instance = kwargs.get('instance')
    headers = {
        'Message-ID': instance.get_message_id(),
        'In-Reply-To': instance.decision.get_message_id(),
        'References': ' '.join((
            instance.decision.get_message_id(),
            instance.get_message_id()))
    }
    headers.update(STANDARD_SENDING_HEADERS)

    instance.decision.note_external_modification()

    observation_manager = ObservationManager()
    org_users = list(instance.decision.organization.users.filter(is_active=True))
    extra_context = dict({"observed": instance})

    if kwargs.get('created', True):
        # All watchers of parent get notified of new feedback.
        observation_manager.send_notifications(org_users, instance, FEEDBACK_NEW, extra_context, headers, from_email=instance.decision.get_email())
    else:
        # An edit by someone other than the author never counts as minor
        if instance.author != instance.editor or not instance.minor_edit:
            observation_manager.send_notifications(org_users, instance, FEEDBACK_CHANGE, extra_context, headers, from_email=instance.decision.get_email())
        else:
            observation_manager.send_notifications(org_users, instance, MINOR_CHANGE, extra_context, headers, from_email=instance.decision.get_email())


@receiver(comment_was_posted, sender=Comment, dispatch_uid="publicweb.models.comment_posted_signal_handler")
def comment_posted_signal_handler(sender, **kwargs):
    """
    If the user wishes to be a watcher, add them as a watcher and send them a
    notification
    """
    comment = kwargs.get('comment')
    post = kwargs['request'].POST.copy()

    decision = comment.content_object.decision
    user = comment.user

    change_observers(post.get('watch', False), decision, user)

    decision.note_external_modification()

    org_users = list(comment.content_object.decision.organization.users.filter(is_active=True))

    send_comment_notifications(comment, org_users)


def actionitem_signal_handler(sender, **kwargs):
    """
    Triggers external update to decision associated with this action item.
    As well as updating the "last-modified" field, this has the nice
    consequence of causing the decision to get re-indexed.
    """
    instance = kwargs.get('instance')
    if isinstance(instance.origin, Decision):
        instance.origin.note_external_modification()

        ACTION = ACTIONITEM_NEW if kwargs['created'] else ACTIONITEM_CHANGE

        org_users = list(instance.origin.organization.users.filter(is_active=True))

        observation_manager = ObservationManager()
        extra_context = dict({"observed": instance})

        headers = {
            'Message-ID': get_action_item_message_id(instance),
            'In-Reply-To': instance.origin.get_message_id(),
            'References': ' '.join((
                instance.origin.get_message_id(),
                get_action_item_message_id(instance)))
        }
        headers.update(STANDARD_SENDING_HEADERS)

        observation_manager.send_notifications(org_users, instance.origin, ACTION, extra_context, headers, from_email=instance.origin.get_email())

# We can't register our ActionItem post-save signal handler, as importing the
# ActionItem model in this file would result in a circular dependency. So
# instead we listen for the ActionItem model class being defined, and register
# the post-save signal handler when it is ready.
@receiver(models.signals.class_prepared, dispatch_uid="publicweb.models.class_prepared_signal_handler")
def class_prepared_signal_handler(sender, **kwargs):
    if sender.__name__ == "ActionItem":
        register = receiver(models.signals.post_save,
                            sender=sender,
                            dispatch_uid="publicweb.models.actionitem_signal_handler")
        register(actionitem_signal_handler)
