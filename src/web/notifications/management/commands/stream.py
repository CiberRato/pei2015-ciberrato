from django.core.management.base import BaseCommand, CommandError
from ...models import StreamTrial


class Command(BaseCommand):
    help = 'This is a TCP receiver from the simulator viewer!'

    def handle(self, *args, **options):
        self.stdout.write('# The script was launched!')
        StreamTrial.add(trial_identifier="9690b514-0895-4091-93ee-c902ac8f872f", message="teste!")