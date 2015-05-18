from django.test import TestCase
from authentication.models import Account
from rest_framework.test import APIClient
from .models import *


class AuthenticationTestCase(TestCase):
    def setUp(self):
        Account.objects.create(email='test@test.com', username='test', first_name='unit', last_name='test',
                               is_staff=True, teaching_institution='testUA')

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

        client.force_authenticate(user=None)