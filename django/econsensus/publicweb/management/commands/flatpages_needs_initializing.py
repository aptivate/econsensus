from django.contrib.flatpages.models import FlatPage
from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    help = 'Decides if the flat pages required for the templates needs initializing'

    def handle_noargs(self, **options):
        """
        We need to have both an /about/ and a /help/ page for this to work.
        """
        about_present = FlatPage.objects.filter(url='/about/').count()
        help_present = FlatPage.objects.filter(url='/help/').count()

        if about_present and help_present:
            self.stdout.write("0\n")
        else:
            self.stdout.write("1\n")
