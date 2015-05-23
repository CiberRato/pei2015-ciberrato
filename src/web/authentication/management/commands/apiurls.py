from django.core.management.base import BaseCommand, CommandError
from ciberonline.urls import urlpatterns


class Command(BaseCommand):
    help = 'List URLs'

    def handle(self, *args, **options):
        print 0 + self.show_urls(urlpatterns)

    def show_urls(self, urllist, path=""):
        count = 0
        for entry in urllist:
            url_print = str(path + entry.regex.pattern)
            print url_print.replace("^", "").replace(".*$", "").replace("$", "")
            count += 1

            if hasattr(entry, 'url_patterns'):
                count += self.show_urls(entry.url_patterns, entry.regex.pattern)
        return count