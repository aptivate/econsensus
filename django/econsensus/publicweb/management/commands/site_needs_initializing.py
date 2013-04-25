from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    args = ''
    help = 'Decides if the Site data needs initializing'

    def handle(self, *args, **kwargs):
        """
        Not as simple as 'are there any Site objects?' because 
        django.contrib.sites automatically creates an example site
        via a post_syncdb handler.
        """
        sites = Site.objects.filter(id=settings.SITE_ID)
        if sites.count() == 0:
            self.stdout.write("1\n")
        elif sites.count() == 1 and sites[0].domain == u'example.com':
            self.stdout.write("1\n")
        else:
            self.stdout.write("0\n")
