from django.core.management.base import BaseCommand, CommandError
from ciberonline.urls import urlpatterns


class Command(BaseCommand):
    help = 'List URLs'

    def __init__(self):
        self.supers = dict()
        self.supers['api/v1/competitions/'] = []
        self.supers['api/v1/agents/'] = []
        self.supers['api/v1/trials/'] = []
        self.supers['api/v1/statistic/'] = []
        self.supers['api/v1/notifications/'] = []
        self.supers['api/v1/teams/'] = []
        self.supers['api/v1/sticky_notes/'] = []
        self.supers['api/v1/auth/'] = []
        self.supers['api/v1/accounts/'] = []

        self.supers['except'] = []

        super(Command, self).__init__()

    def handle(self, *args, **options):
        # add manual urls
        self.supers['api/v1/auth/'] += ['api/v1/auth/logout/']
        self.supers['api/v1/auth/'] += ['api/v1/auth/login/']
        self.supers['api/v1/auth/'] += ['api/v1/auth/login/']
        self.supers['api/v1/auth/'] += ['api/v1/get_captcha/']
        self.supers['api/v1/auth/'] += ['check/email/(?P<token>.+)/']

        # except
        self.supers['except'] += ['idp/']
        self.supers['except'] += ['panel/']
        self.supers['except'] += ['admin/']
        self.supers['except'] += ['api-auth/']
        self.supers['except'] += ['api-auth/login/']
        self.supers['except'] += ['api-auth/logout/']
        self.supers['except'] += ['api-auth/']
        self.supers['except'] += ['captcha/']
        self.supers['except'] += ['captcha/image/(?P<key>\w+)/']
        self.supers['except'] += ['captcha/audio/(?P<key>\w+)/']
        self.supers['except'] += ['captcha/image/(?P<key>\w+)@2/']
        self.supers['except'] += ['captcha/refresh/']
        self.supers['except'] += ['api/v1/']
        
        print 0 + self.show_urls(urlpatterns)

    def show_urls(self, urllist, path=""):
        count = 0
        for entry in urllist:
            url_print = str(path + entry.regex.pattern)
            url = url_print.replace("^", "").replace(".*$", "").replace("$", "")

            for key, value in self.supers.iteritems():
                if url.startswith(key):
                    self.supers[key] += [url]

            in_supers = False
            for key, value in self.supers.iteritems():
                if url in value:
                    in_supers = True
                    break

            if not in_supers:
                print url

            count += 1

            if hasattr(entry, 'url_patterns'):
                count += self.show_urls(entry.url_patterns, entry.regex.pattern)
        return count