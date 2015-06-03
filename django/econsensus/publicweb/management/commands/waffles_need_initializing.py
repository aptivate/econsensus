from waffle import Switch, Flag, Sample
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    args = ''
    help = 'Decides if the Waffle data needs initializing'

    def handle(self, *args, **kwargs):
        """ We will initialize waffles if no switches/flags/samples exist. """
        switches = Switch.objects.all()
        flags = Flag.objects.all()
        samples = Sample.objects.all()
        if not switches and not flags and not samples:
            self.stdout.write("1\n")
        else:
            self.stdout.write("0\n")
