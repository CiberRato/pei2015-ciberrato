from django.test import TestCase
from authentication.models import Account
from rest_framework.test import APIClient
from .models import *
from authentication.models import TeamMember


class AuthenticationTestCase(TestCase):
    def setUp(self):
        user = Account.objects.create(email='test@test.com', username='test', first_name='unit', last_name='test',
                                      is_staff=True, teaching_institution='testUA')
        team = Team.objects.create(name="XPTO1")
        TeamMember.objects.create(account=user, team=team)
        team = Team.objects.create(name="XPTO2")
        TeamMember.objects.create(account=user, team=team)

    def test_sticky_note(self):
        user = Account.objects.get(email='test@test.com')
        client = APIClient()
        client.force_authenticate(user=user)

        # create 10 broadcast notifications
        for i in range(0, 11):
            NotificationBroadcast.add(channel="broadcast", status="ok", message="ok"+str(i))

        # get broadcast notifications
        url = "/api/v1/notifications/broadcast/"
        response = client.get(path=url)

        i = 0
        for response in response.data:
            self.assertEqual(response["message"], u"{'status': 200, 'content': 'ok"+str(6+i)+"', 'trigger': ''}")
            i += 1

        # create 10 admin notifications
        for i in range(11, 22):
            NotificationBroadcast.add(channel="admin", status="ok", message="ok"+str(i))

        # get admin notifications
        url = "/api/v1/notifications/admin/"
        response = client.get(path=url)

        i = 0
        for response in response.data:
            self.assertEqual(response["message"], u"{'status': 200, 'content': 'ok" + str(17 + i) + "', 'trigger': ''}")
            i += 1

        # create 10 user notifications
        for i in range(22, 33):
            NotificationUser.add(user=user, status="ok", message="ok" + str(i))

        # get user notifications
        url = "/api/v1/notifications/user/"
        response = client.get(path=url)

        i = 0
        for response in response.data:
            self.assertEqual(response["message"], u"{'status': 200, 'content': 'ok" + str(28 + i) + "', 'trigger': ''}")
            i += 1

        # create 10 team notifications
        team = Team.objects.get(name="XPTO1")

        for i in range(33, 44):
            NotificationTeam.add(team=team, status="ok", message="ok" + str(i))

        # create 10 team notifications
        team = Team.objects.get(name="XPTO2")

        for i in range(33, 44):
            NotificationTeam.add(team=team, status="ok", message="ok" + str(i))

        # get user notifications
        url = "/api/v1/notifications/teams/"
        response = client.get(path=url)
        print response

        # i = 0
        # for response in response.data:
            # print response
            # self.assertEqual(response["message"],
            # u"{'status': 200, 'content': 'ok" + str(28 + i) + "', 'trigger': ''}")
            # i += 1

        client.force_authenticate(user=None)