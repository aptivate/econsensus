from django.test import SimpleTestCase  
from django_dynamic_fixture import N
from publicweb.models import Decision, Feedback, comment_signal_handler
from django.contrib.auth.models import User
from mock import patch, MagicMock
from django.contrib.comments.models import Comment

class AddCommentsTest(SimpleTestCase):

    @patch('notification.models.observe')
    @patch('publicweb.models.ObservationManager.send_notifications', 
           new=MagicMock())
    def test_comment_post_save_handler_adds_user_as_watcher_if_created(self, 
        observe):
        user_1 = N(User, id=1)
        decision = N(Decision, author=user_1, editor=user_1, id=1)
        feedback = N(Feedback, author=user_1, editor=user_1, decision=decision,
                     id=1)
        comment = N(Comment, user=N(User, id=2))
        comment.content_object = feedback
        comment_signal_handler(sender=Comment, created=True, instance=comment)
        observe.assert_called_with(decision, comment.user, "comment_change")
