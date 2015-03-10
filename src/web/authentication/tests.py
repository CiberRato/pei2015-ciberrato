from django.test import TestCase
from authentication.models import Account

from rest_framework.test import APIClient
from collections import OrderedDict


class AuthenticationTestCase(TestCase):
    def setUp(self):
        Account.objects.create(email='test@test.com', username='test', first_name='unit', last_name='test',
                               teaching_institution='testUA')

    def test_account_details(self):
        account = Account.objects.get(email='test@test.com')
        self.assertEqual(account.email, 'test@test.com')
        self.assertEqual(account.username, 'test')
        self.assertEqual(account.first_name, 'unit')
        self.assertEqual(account.last_name, 'test')
        self.assertEqual(account.teaching_institution, 'testUA')

    def test_create_account(self):
        user = Account.objects.get(email='test@test.com')
        client = APIClient()

        client.force_authenticate(user=user)

        url = "/api/v1/accounts/"

        response = client.get(url)
        self.assertEqual(response.data, [OrderedDict(
            [('id', 1), ('email', u'test@test.com'), ('username', u'test'), ('teaching_institution', u'testUA'),
             ('first_name', u'unit'), ('last_name', u'test')])])

        data = {'email': 'test1@test.com', 'username': 'test1', 'first_name': 'unit', 'last_name': 'test',
                'teaching_institution': 'testUA'}
        response = client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, 201)

        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        url = "/api/v1/accounts/test/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(dict(response.data),
                         {'id': 1, 'email': u'test@test.com', 'username': u'test', 'teaching_institution': u'testUA',
                          'first_name': u'unit', 'last_name': u'test'})

        url = "/api/v1/accounts/test/"
        data = {'email': 'test2@test.com', 'first_name': 'unit', 'last_name': 'test',
                'teaching_institution': 'testUA'}
        response = client.put(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(dict(response.data), {'status': 'Updated', 'message': 'Account updated.'})

        url = "/api/v1/accounts/test/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(dict(response.data), {'username': u'test', 'first_name': u'unit', 'last_name': u'test',
                                               'teaching_institution': u'testUA', 'email': u'test2@test.com', 'id': 1})

        client.login(email='test@test.com')
        client.logout()

        client.force_authenticate(user=None)