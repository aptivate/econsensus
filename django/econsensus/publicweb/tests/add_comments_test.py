from django.test import SimpleTestCase  
from django_dynamic_fixture import N
from publicweb.models import Decision, Feedback, comment_signal_handler
from django.contrib.auth.models import User
from mock import patch, MagicMock
from custom_comments.forms import CustomCommentForm
from django.utils.crypto import salted_hmac
from django.contrib.comments.models import Comment
from django.test.client import RequestFactory
import time

class AddCommentsTest(SimpleTestCase):

    @patch('notification.models.observe')
    @patch('publicweb.models.ObservationManager.send_notifications', 
           new=MagicMock())
    def test_comment_was_posted_adds_user_as_watcher_if_watch_selected(self, 
        observe):
        user_1 = N(User, id=1)
        decision = N(Decision, author=user_1, editor=user_1, id=1)
        feedback = N(Feedback, author=user_1, editor=user_1, decision=decision,
                     id=1)

        content_type = "publicweb.feedback"
        object_pk = "1"
        timestamp = str(int(time.time()))
        info = (content_type, object_pk, timestamp) 
        key_salt = "django.contrib.forms.CommentSecurityForm"
        value = "-".join(info)
        security_hash = salted_hmac(key_salt, value).hexdigest()
        data = {
            'content_type': content_type,
            'object_pk': object_pk,
            'timestamp': timestamp,
            'security_hash': security_hash,
            'name': user_1.first_name,
            'email': user_1.email,
            'url': "",
            'comment': "Hello",
            'honeypot': "",
            'watch': "True"  
        }
        form = CustomCommentForm(target_object=feedback, data=data)
        
        form.is_valid()

        comment = form.get_comment_object()
        comment.content_object = feedback
        comment.user = user_1
        request = RequestFactory().post('/', data)
        comment_signal_handler(Comment, request=request, comment=comment)
        observe.assert_called_with(decision, user_1, "decision_change")
    
    @patch('notification.models.observe')
    @patch('publicweb.models.ObservationManager.send_notifications', 
           new=MagicMock())
    def test_comment_was_posted_doesnt_add_user_as_watcher_if_watch_not_selected(
        self, observe
    ):
        user_1 = N(User, id=1)
        decision = N(Decision, author=user_1, editor=user_1, id=1)
        feedback = N(Feedback, author=user_1, editor=user_1, decision=decision,
                     id=1)

        content_type = "publicweb.feedback"
        object_pk = "1"
        timestamp = str(int(time.time()))
        info = (content_type, object_pk, timestamp) 
        key_salt = "django.contrib.forms.CommentSecurityForm"
        value = "-".join(info)
        security_hash = salted_hmac(key_salt, value).hexdigest()
        data = {
            'content_type': content_type,
            'object_pk': object_pk,
            'timestamp': timestamp,
            'security_hash': security_hash,
            'name': user_1.first_name,
            'email': user_1.email,
            'url': "",
            'comment': "Hello",
            'honeypot': "",
        }
        form = CustomCommentForm(target_object=feedback, data=data)
        
        form.is_valid()

        comment = form.get_comment_object()
        comment.content_object = feedback
        comment.user = user_1
        request = RequestFactory().post('/', data)
        comment_signal_handler(Comment, request=request, comment=comment)
        self.assertFalse(observe.called)
    
    def test_comments_form_has_watch_field(self):
        form = CustomCommentForm(target_object=N(Feedback, id=1))
        self.assertIn('watch', form.fields)
        