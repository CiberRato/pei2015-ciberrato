from django.core.management.base import BaseCommand, CommandError
from ...models import StreamTrial
import socket


class Command(BaseCommand):
    help = 'This is a TCP receiver from the simulator viewer!'

    def handle(self, *args, **options):
        self.stdout.write('[STREAM] The script was launched!')

        while True:
            self.stdout.write('[STREAM] Waiting for new streaming!')

            host = "127.0.0.1"
            port = 10000

            sim_viewer_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sim_viewer_connect.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sim_viewer_connect.bind((host, port))
            sim_viewer_connect.listen(1)
            sim_viewer, addr = sim_viewer_connect.accept()

            identifier = sim_viewer.recv(1024)
            self.stdout.write('[STREAM] Trial ' + str(identifier) + ' is now streaming!')

            while True:
                data = sim_viewer.recv(1024 * 8)
                if str(data) == "END":
                    break

                StreamTrial.add(trial_identifier=identifier, message=data)

            sim_viewer_connect.shutdown(socket.SHUT_RDWR)
            sim_viewer_connect.close()
            sim_viewer.shutdown(socket.SHUT_RDWR)
            sim_viewer.close()
            
            self.stdout.write('[STREAM] Trial ' + str(identifier) + ' ended the streaming!')