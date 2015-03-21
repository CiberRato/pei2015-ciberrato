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
        rsp = response.data
        del rsp[0]['updated_at']
        del rsp[0]['created_at']
        self.assertEqual(rsp, [OrderedDict(
            [('email', u'test@test.com'), ('username', u'test'), ('teaching_institution', u'testUA'),
             ('first_name', u'unit'), ('last_name', u'test')])])

        url = "/api/v1/account_by_first_name/unit/"
        response = client.get(url)
        rsp = response.data
        del rsp[0]['updated_at']
        del rsp[0]['created_at']
        self.assertEqual(rsp, [OrderedDict(
            [('email', u'test@test.com'), ('username', u'test'), ('teaching_institution', u'testUA'),
             ('first_name', u'unit'), ('last_name', u'test')])])
        self.assertEqual(response.status_code, 200)

        url = "/api/v1/account_by_last_name/test/"
        response = client.get(url)
        rsp = response.data
        del rsp[0]['updated_at']
        del rsp[0]['created_at']
        self.assertEqual(rsp, [OrderedDict(
            [('email', u'test@test.com'), ('username', u'test'), ('teaching_institution', u'testUA'),
             ('first_name', u'unit'), ('last_name', u'test')])])
        self.assertEqual(response.status_code, 200)

        url = "/api/v1/accounts/"
        data = {'email': 'test1@test.com', 'username': 'test1', 'first_name': 'unit', 'last_name': 'test',
                'teaching_institution': 'testUA'}
        response = client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, 201)

        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        url = "/api/v1/accounts/test1/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = dict(response.data)
        del rsp['updated_at']
        del rsp['created_at']
        self.assertEqual(rsp,
                         {'email': u'test1@test.com', 'username': u'test1', 'teaching_institution': u'testUA',
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
        rsp = dict(response.data)
        del rsp['updated_at']
        del rsp['created_at']
        self.assertEqual(rsp, {'username': u'test', 'first_name': u'unit', 'last_name': u'test',
                               'teaching_institution': u'testUA', 'email': u'test2@test.com'})

        # create a group
        url = "/api/v1/groups/crud/"
        data = {'name': 'TestGroup', 'max_members': 10}
        response = client.post(path=url, data=data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict([('name', u'TestGroup'), ('max_members', 10)]))

        url = "/api/v1/accounts/test/"
        response = client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'status': 'Deleted', 'message': 'The account has been deleted.'})

        url = "/api/v1/accounts/test/"
        response = client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {u'detail': u'Not found.'})

        client.login(email='test@test.com')
        client.logout()

        client.force_authenticate(user=None)