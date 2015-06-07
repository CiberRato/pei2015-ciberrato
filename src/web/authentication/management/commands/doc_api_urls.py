from django.core.management.base import BaseCommand
import json
import apiurls


class Command(BaseCommand):
    help = 'List URLs to make one doc'

    def __init__(self):
        self.cmd = apiurls.Command()
        super(Command, self).__init__()

    def handle(self, *args, **options):
        output = json.loads(self.cmd.handle())
        output_string = ""

        for key, value in output.iteritems():
            output_string += "**" + key + "**\n"
            output_string += "*" + str(value['count']) + " endpoints*\n\n"

            for key, value in value.iteritems():
                if key == "urls":
                    for url in value:
                        output_string += " - `" + url["url"] + "`\n"

            output_string += "\n"
        print output_string