from django.contrib.comments.forms import CommentForm, COMMENT_MAX_LENGTH
from django.utils.translation import ungettext, ugettext_lazy as _
from django import forms
from parsley.decorators import parsleyfy
from django.forms.fields import BooleanField


"""
The form is customised so that the id of every field is unique
This ensures html validation passes (ie no duplicate ids) when
there are multiple comment forms on a single page.
"""
@parsleyfy
class CustomCommentForm(CommentForm):
    def __init__(self, target_object, data=None, initial=None):
        super(CustomCommentForm, self).__init__(target_object, data, initial)
        self.auto_id = "%s_" + str(target_object.id)

    comment = forms.CharField(label=_('Comment'), widget=forms.Textarea(attrs={'rows':4}),
                                    max_length=COMMENT_MAX_LENGTH)
    watch = BooleanField(required=False, label="Watch this conversation",
        help_text="If you check this box, you will receive notifications about "
        "further updates to this conversation. This overrides your notification"
        " settings.", initial=True)
