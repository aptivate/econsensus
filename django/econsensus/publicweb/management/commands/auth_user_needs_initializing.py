from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    args = ''
    help = 'Decides if the User data needs initializing'

    def handle(self, *args, **kwargs):
        """
        Not as simple as 'are there any users in the table?' because django-guardian creates
        User called AnonymousUser via post_syncdb signal handler.
        """
        users = User.objects.all()
        if not users or users.count() == 1 and users[0].id == settings.ANONYMOUS_USER_ID:
            self.stdout.write("1\n")
        else:
            self.stdout.write("0\n")

