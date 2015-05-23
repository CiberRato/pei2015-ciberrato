from django.core.management.base import BaseCommand, CommandError
from ...models import NotificationBroadcast


class Command(BaseCommand):
    help = 'This is a TCP receiver from the simulator viewer!'

    def handle(self, *args, **options):
        self.stdout.write('# The script was launched!')
        NotificationBroadcast.add(channel="broadcast", status="ok", message="teste!")