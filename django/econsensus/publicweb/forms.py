# Create your forms here.

from django import forms
from models import Decision, Feedback
from django.contrib.auth.models import User


from django.utils.translation import ugettext_lazy as _
from django.forms.fields import ChoiceField
from django.forms.widgets import RadioSelect

from widgets import JQueryUIDateWidget

from publicweb.models import NotificationSettings, change_observers, \
    additional_message_required, send_decision_notifications

from parsley.decorators import parsleyfy
from actionitems.forms import ActionItemCreateForm, ActionItemUpdateForm
from publicweb.extra_models import MAIN_ITEMS_NOTIFICATIONS_ONLY
from actionitems.models import ActionItem


class YourDetailsForm(forms.ModelForm):

    class Meta:
        model = User
        exclude = ('is_staff', 'is_superuser', 'is_active', 'last_login',
                'date_joined', 'groups', 'user_permissions', 'password')

    def clean_email(self):
        if self.instance.email == self.cleaned_data['email']:
            return self.cleaned_data['email']
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(
                _(
                    "This email address is already in use. Please supply a "
                    "different email address."
                )
            )
        return self.cleaned_data['email']


class NotificationsForm(forms.ModelForm):
    watch = forms.BooleanField(
        required=False,
        label=_("Watch this conversation"),
        help_text=_(
            "If you check this box, you will receive notifications about "
            "further updates to this conversation. This overrides your "
            "notification settings."
        ),
        initial=True
    )

    def get_decision(self):
        raise NotImplementedError

    def change_observers(self, decision, watcher):
        watch = self.cleaned_data.get('watch', False)
        change_observers(watch, decision, watcher)

    def save(self, commit=True):
        # The only time a decision won't have an id is when it's created.
        # In this case, we'll want to handle it in the post save handler
        decision = self.get_decision()
        if commit and decision.id:
            user = self.instance.editor or self.instance.author
            self.change_observers(decision, user)
        return super(NotificationsForm, self).save(commit)


class FeedbackForm(NotificationsForm):
    minor_edit = forms.BooleanField(required=False, initial=False)

    def get_decision(self):
        return self.instance.decision

    class Meta:
        model = Feedback
        exclude = ("decision",)


@parsleyfy
class DecisionForm(NotificationsForm):

    watch = forms.BooleanField(required=False, initial=True)
    minor_edit = forms.BooleanField(required=False, initial=False)

    def get_decision(self):
        return self.instance

    def save(self, commit=True):
        created = not self.instance.id
        decision = super(DecisionForm, self).save(commit)

        send_new_message = additional_message_required(
           decision.author or decision.editor,
           decision, MAIN_ITEMS_NOTIFICATIONS_ONLY)
        if commit and created:
            self.change_observers(decision, decision.author)
            if send_new_message:
                send_decision_notifications(decision, [decision.author])
        return decision

    class Meta:
        model = Decision
        exclude = ('organization',)
        widgets = {
           'decided_date': JQueryUIDateWidget,
           'effective_date': JQueryUIDateWidget,
           'review_date': JQueryUIDateWidget,
           'expiry_date': JQueryUIDateWidget,
           'archived_date': JQueryUIDateWidget,
           'deadline': JQueryUIDateWidget
        }


EXTRA_CHOICE = (3, _('All'))  # pylint: disable=E1102


@parsleyfy
class EconsensusActionItemCreateForm(ActionItemCreateForm):
    pass
# TODO: Sort and filter forms have nothing to do with the app itself.
# Move to site when site and app are split.


@parsleyfy
class EconsensusActionItemUpdateForm(ActionItemUpdateForm):
    pass


class FilterForm(forms.Form):
    # this seems clunky...
    list_choices = list(Decision.STATUS_CHOICES)
    list_choices.append(EXTRA_CHOICE)
    FILTER_CHOICES = tuple(list_choices)
    filtar = ChoiceField(choices=FILTER_CHOICES,
                         label=_('Status'),  # pylint: disable=E1102
                         initial=EXTRA_CHOICE[0],
                         required=False,
                         widget=forms.Select(
                             attrs={'onchange': 'this.form.submit()'}
                         ))


class NotificationSettingsForm(forms.ModelForm):

    class Meta:
        model = NotificationSettings
        exclude = ('user', 'organization')
        widgets = {
            'notification_level': RadioSelect
        }