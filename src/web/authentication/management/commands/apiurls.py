from django.core.management.base import BaseCommand, CommandError
from ciberonline.urls import urlpatterns


class Command(BaseCommand):
    help = 'List URLs'

    class SuperURL:
        def __init__(self, help_text):
            self.count = 0
            self.help_text = help_text
            self.urls = []

    def __init__(self):
        self.supers = dict()
        self.supers['api/v1/competitions/'] = self.SuperURL("Competitions")
        self.supers['api/v1/agents/'] = self.SuperURL("Agents")
        self.supers['api/v1/trials/'] = self.SuperURL("Trials")
        self.supers['api/v1/statistics/'] = self.SuperURL("Statistics")
        self.supers['api/v1/notifications/'] = self.SuperURL("Notifications")
        self.supers['api/v1/teams/'] = self.SuperURL("Teams")
        self.supers['api/v1/sticky_notes/'] = self.SuperURL("Sticky notes")
        self.supers['api/v1/auth/'] = self.SuperURL("Authentication")
        self.supers['api/v1/accounts/'] = self.SuperURL("Accounts")

        self.supers['except'] = self.SuperURL("except")

        super(Command, self).__init__()

    def handle(self, *args, **options):
        # add manual urls
        self.supers['api/v1/auth/'].urls += ['api/v1/auth/logout/']
        self.supers['api/v1/auth/'].urls += ['api/v1/auth/login/']
        self.supers['api/v1/auth/'].urls += ['api/v1/auth/login/']
        self.supers['api/v1/auth/'].urls += ['api/v1/get_captcha/']
        self.supers['api/v1/auth/'].urls += ['check/email/(?P<token>.+)/']
        self.supers['api/v1/auth/'].urls += ['api/v1/password_recover/']
        self.supers['api/v1/auth/'].urls += ['api/v1/password_recover/request/']
        self.supers['api/v1/auth/'].urls += ['api/v1/login_to/(?P<username>[/.]+)/']

        self.supers['api/v1/accounts/'].urls += ['api/v1/change_password/(?P<username>[/.]+)/']
        self.supers['api/v1/accounts/'].urls += ['api/v1/account_by_first_name/(?P<pk>[/.]+)/']
        self.supers['api/v1/accounts/'].urls += ['api/v1/account_by_last_name/(?P<pk>[/.]+)/']
        self.supers['api/v1/accounts/'].urls += ['api/v1/toggle_staff/(?P<username>[/.]+)/']
        self.supers['api/v1/accounts/'].urls += ['api/v1/toggle_super_user/(?P<username>[/.]+)/']
        self.supers['api/v1/accounts/'].urls += ['api/v1/toggle_super_user/(?P<username>[/.]+)/']
        self.supers['api/v1/accounts/'].urls += ['api/v1/me/']
        self.supers['api/v1/accounts/'].urls += ['api/v1/me/']

        self.supers['api/v1/competitions/'].urls += ['api/v1/round_resources/']
        self.supers['api/v1/competitions/'].urls += ['api/v1/set_round_file/(?P<competition_name>.+)/(?P<round_name>.+)/(?P<param>.+)/']
        self.supers['api/v1/competitions/'].urls += ['api/v1/resources_file/']

        # except
        self.supers['except'].urls += ['idp/']
        self.supers['except'].urls += ['panel/']
        self.supers['except'].urls += ['admin/']
        self.supers['except'].urls += ['api-auth/']
        self.supers['except'].urls += ['api-auth/login/']
        self.supers['except'].urls += ['api-auth/logout/']
        self.supers['except'].urls += ['api-auth/']
        self.supers['except'].urls += ['captcha/']
        self.supers['except'].urls += ['captcha/image/(?P<key>\w+)/']
        self.supers['except'].urls += ['captcha/audio/(?P<key>\w+)/']
        self.supers['except'].urls += ['captcha/image/(?P<key>\w+)@2/']
        self.supers['except'].urls += ['captcha/refresh/']
        self.supers['except'].urls += ['api/v1/']

        print 0 + self.show_urls(urlpatterns)
        # print self.supers['api/v1/competitions/'].count
        # print self.supers['api/v1/competitions/'].urls

    def show_urls(self, urllist, path="", verify_supers=False):
        count = 0
        for entry in urllist:
            url_print = str(path + entry.regex.pattern)
            url = url_print.replace("^", "").replace(".*$", "").replace("$", "")

            for key, value in self.supers.iteritems():
                if url.startswith(key):
                    self.supers[key].urls += [url]
                    self.supers[key].count += 1

            if verify_supers:
                in_supers = False
                for key, value in self.supers.iteritems():
                    if url in value.urls:
                        in_supers = True
                        break

                if not in_supers:
                    print url

            count += 1

            if hasattr(entry, 'url_patterns'):
                count += self.show_urls(entry.url_patterns, entry.regex.pattern, verify_supers=verify_supers)
        return count