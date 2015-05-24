from django.core.management.base import BaseCommand, CommandError
from ciberonline.urls import urlpatterns
from django.core.urlresolvers import RegexURLPattern
import markdown
from inflector import English, Inflector
import json


class Command(BaseCommand):
    help = 'List URLs'

    class SuperURL:
        def __init__(self, help_text):
            self.count = 0
            self.help_text = help_text
            self.urls = []

    class SlaveURL:
        def __init__(self, url, doc, name):
            global inflector
            self.url = url
            if doc is not None:
                self.doc = markdown.markdown(doc.replace("    ", ""))
            else:
                self.doc = ""
            inflector = Inflector(English)
            self.name = inflector.humanize(word=name.replace("-", " "))

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

        self.manual = dict()

        self.count = 0

        super(Command, self).__init__()

    def handle(self, *args, **options):
        # add manual urls
        self.manual['api/v1/auth/logout/'] = 'api/v1/auth/'

        self.manual['api/v1/auth/login/'] = 'api/v1/auth/'
        self.manual['api/v1/auth/login/'] = 'api/v1/auth/'
        self.manual['api/v1/get_captcha/'] = 'api/v1/auth/'
        self.manual['check/email/(?P<token>.+)/'] = 'api/v1/auth/'
        self.manual['api/v1/password_recover/'] = 'api/v1/auth/'
        self.manual['api/v1/password_recover/request/'] = 'api/v1/auth/'
        self.manual['api/v1/login_to/(?P<username>[/.]+)/'] = 'api/v1/auth/'

        self.manual['api/v1/change_password/(?P<username>[/.]+)/'] = 'api/v1/accounts/'
        self.manual['api/v1/account_by_first_name/(?P<pk>[/.]+)/'] = 'api/v1/accounts/'
        self.manual['api/v1/account_by_last_name/(?P<pk>[/.]+)/'] = 'api/v1/accounts/'
        self.manual['api/v1/toggle_staff/(?P<username>[/.]+)/'] = 'api/v1/accounts/'
        self.manual['api/v1/toggle_super_user/(?P<username>[/.]+)/'] = 'api/v1/accounts/'
        self.manual['api/v1/toggle_super_user/(?P<username>[/.]+)/'] = 'api/v1/accounts/'
        self.manual['api/v1/me/'] = 'api/v1/accounts/'

        self.manual['api/v1/round_resources/'] = 'api/v1/competitions/'
        self.manual['api/v1/set_round_file/(?P<competition_name>.+)/(?P<round_name>.+)/(?P<param>.+)/'] = 'api/v1/competitions/'
        self.manual['api/v1/resources_file/'] = 'api/v1/competitions/'

        self.__arrange_urls__(urlpatterns)
        print self.to_json()
        # print self.supers['api/v1/auth/'].count
        # print self.supers['api/v1/auth/'].urls[0].doc
        # print self.supers['api/v1/auth/'].urls[0].name

    def to_json(self):
        json_var = dict()
        for key, value in self.supers.iteritems():
            sp = dict()
            sp['count'] = value.count
            sp['help_text'] = value.help_text
            sp['urls'] = []

            for slave in value.urls:
                sl = dict()
                sl['url'] = slave.url
                sl['doc'] = slave.doc
                sl['name'] = slave.name
                sp['urls'] += [sl]
            json_var[key] = sp
        return json_var

    def __arrange_urls__(self, urllist, path="", verify_supers=False):
        for entry in urllist:
            if isinstance(entry, RegexURLPattern):
                url_print = str(path + entry.regex.pattern)
                url = url_print.replace("^", "").replace(".*$", "").replace("$", "")

                found = False

                # save in the super list
                for key, value in self.supers.iteritems():
                    if url.startswith(key):
                        self.supers[key].urls += [self.SlaveURL(url=url, doc=entry.callback.__doc__, name=entry.name)]
                        self.supers[key].count += 1
                        found = True
                        break

                # manual URLs
                if not found:
                    for key, value in self.manual.iteritems():
                        if url == key:
                            self.supers[value].urls += [self.SlaveURL(url=url, doc=entry.callback.__doc__,
                                                                      name=entry.name)]
                            self.supers[value].count += 1
                            break

                # verify if has new URls
                if verify_supers:
                    in_supers = False
                    for key, value in self.supers.iteritems():
                        if url in value.urls:
                            in_supers = True
                            break

                    if not in_supers:
                        print url

                self.count += 1

            if hasattr(entry, 'url_patterns'):
                self.__arrange_urls__(entry.url_patterns, entry.regex.pattern, verify_supers=verify_supers)