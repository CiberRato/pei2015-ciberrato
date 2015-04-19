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
        rsp = response.data['results']
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
        data = {'email': 'test1@test.com', 'username': 'test1', 'password': 'rei12345678',
                'confirm_password': 'rei12345678', 'first_name': 'unit', 'last_name': 'test',
                'teaching_institution': 'testUA'}
        response = client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, 201)

        # change password with other user
        url = "/api/v1/change_password/test1/"
        data = {'password': '1234', 'confirm_password': '1234'}
        response = client.put(url, data)
        self.assertEqual(response.data, {'status': 'Forbidden!', 'message': 'Ups, what?'})
        self.assertEqual(response.status_code, 403)

        # change password with the user
        url = "/api/v1/change_password/test/"
        data = {'password': '1234', 'confirm_password': '1234'}
        response = client.put(url, data)
        self.assertEqual(response.data, {'status': 'Bad Request', 'message': {
        'confirm_password': [u'Ensure this value has at least 8 characters (it has 4).'],
        'password': [u'Ensure this value has at least 8 characters (it has 4).']}})
        self.assertEqual(response.status_code, 400)

        # change correctly the password
        url = "/api/v1/change_password/test/"
        data = {'password': '123456789', 'confirm_password': '123456789'}
        response = client.put(url, data)
        self.assertEqual(response.data, {'status': 'Updated', 'message': 'Account updated.'})
        self.assertEqual(response.status_code, 200)

        # get informations
        url = "/api/v1/accounts/"
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

        # update a user to staff member
        user.is_staff = True
        user.save()

        url = "/api/v1/toggle_staff/test/"
        response = client.put(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status":"Updated","message":"Account updated, is staff? False"})
        a = Account.objects.get(username="test")
        self.assertEqual(a.is_staff, False)

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

    def test_url_slug(self):
        client = APIClient()

        # try to create with username error
        url = "/api/v1/accounts/"
        data = {'email': 'test1@test.com', 'username': 'test.1', 'first_name': 'unit', 'last_name': 'test',
                'teaching_institution': 'testUA'}
        response = client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, 400)

        # try to create with first_name error
        url = "/api/v1/accounts/"
        data = {'email': 'test1@test.com', 'username': 'test1', 'first_name': 'un.it', 'last_name': 'test',
                'teaching_institution': 'testUA'}
        response = client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, 400)

        # try to create with last_name error
        url = "/api/v1/accounts/"
        data = {'email': 'test1@test.com', 'username': 'test1', 'first_name': 'unit', 'last_name': 'tes.t',
                'teaching_institution': 'testUA'}
        response = client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, 400)

        client.force_authenticate(user=None)

    def test_required_users(self):
        client = APIClient()
        user = Account.objects.get(email='test@test.com')
        client.force_authenticate(user=user)

        # try to create with username error
        url = "/api/v1/accounts/"
        data = {'email': 'test', 'username': '', 'first_name': '', 'last_name': '',
                'teaching_institution': ''}
        response = client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, 400)

        # the fields can not be blank
        url = "/api/v1/accounts/test/"
        data = {'email': '', 'username': '', 'first_name': '', 'last_name': '',
                'teaching_institution': ''}
        response = client.put(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(dict(response.data), {'status': 'Bad Request',
                                               'message': {'first_name': [u'This field may not be blank.'],
                                                           'last_name': [u'This field may not be blank.'],
                                                           'email': [u'This field may not be blank.'],
                                                           'teaching_institution': [u'This field may not be blank.']}})

