from collections import OrderedDict

from django.test import TestCase
from authentication.models import Account
from rest_framework.test import APIClient
from captcha.models import CaptchaStore


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
        user.is_staff = True
        user.save()

        client = APIClient()
        client.force_authenticate(user=user)

        url = "/api/v1/accounts/"
        response = client.get(url)
        rsp = response.data["results"]
        del rsp[0]['updated_at']
        del rsp[0]['created_at']
        self.assertEqual(rsp, [OrderedDict([('email', u'test@test.com'), ('username', u'test'), ('teaching_institution', u'testUA'), ('first_name', u'unit'), ('last_name', u'test'), ('is_staff', True), ('is_superuser', False)])])

        user.is_staff = False
        user.save()
        # get captcha
        url = "/api/v1/get_captcha/"
        response = client.get(path=url)
        captcha = CaptchaStore.objects.get(hashkey=response.data["new_cptch_key"])

        url = "/api/v1/accounts/"
        data = {'email': 'test1@test.com', 'username': 'test1', 'password': 'rei12345678',
                'confirm_password': 'rei12345678', 'first_name': 'unit', 'last_name': 'test',
                'teaching_institution': 'testUA', 'hashkey': response.data["new_cptch_key"],
                'response': captcha.response}
        response = client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, 201)

        # change password with other user
        url = "/api/v1/change_password/test1/"
        data = {'password': '1234', 'confirm_password': '1234'}
        response = client.put(url, data)
        self.assertEqual(response.data, {u'detail': u'Ups, what?'})
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
        self.assertEqual(response.status_code, 403)

        url = "/api/v1/accounts/test1/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = dict(response.data)
        del rsp['updated_at']
        del rsp['created_at']
        self.assertEqual(rsp, {'username': u'test1', 'first_name': u'unit', 'last_name': u'test', 'is_superuser': False,
                               'is_staff': False, 'teaching_institution': u'testUA', 'email': u'test1@test.com'})

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
        self.assertEqual(rsp, {'username': u'test', 'first_name': u'unit', 'last_name': u'test', 'is_superuser': False,
                               'is_staff': False, 'teaching_institution': u'testUA', 'email': u'test2@test.com'})

        # update a user to staff member
        user.is_staff = True
        user.save()

        url = "/api/v1/toggle_staff/test/"
        response = client.put(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "Updated", "message": "Account updated, is staff? False"})
        a = Account.objects.get(username="test")
        self.assertEqual(a.is_staff, False)

        # update a user to super user
        user.is_superuser = True
        user.save()

        url = "/api/v1/toggle_super_user/test/"
        response = client.put(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "Updated", "message": "Account updated, is super user? False"})
        a = Account.objects.get(username="test")
        self.assertEqual(a.is_superuser, False)

        # login to different user
        url = "/api/v1/login_to/test1/"
        response = client.get(path=url)
        rsp = dict(response.data)
        del rsp['updated_at']
        del rsp['created_at']
        self.assertEqual(rsp, {'username': u'test1', 'first_name': u'unit', 'last_name': u'test', 'is_superuser': False,
                               'is_staff': False, 'teaching_institution': u'testUA', 'email': u'test1@test.com'})

        # see if the user is currently logged in
        url = "/api/v1/me/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        # create a team
        url = "/api/v1/teams/crud/"
        data = {'name': 'TestTeam', 'max_members': 10}
        response = client.post(path=url, data=data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict([('name', u'TestTeam'), ('max_members', 10)]))

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

        # see the users list
        url = "/api/v1/accounts/"
        response = client.get(path=url)
        self.assertEqual(response.data, {u'detail': u"You don't have permissions to see this list!"})

        # the fields can not be blank
        url = "/api/v1/accounts/test/"
        data = {'email': '', 'username': '', 'first_name': '', 'last_name': '',
                'teaching_institution': ''}
        response = client.put(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(dict(response.data), {"status":"Bad Request","message":{"username":["This field may not be blank."],"first_name":["This field may not be blank."],"last_name":["This field may not be blank."],"email":["This field may not be blank."],"teaching_institution":["This field may not be blank."]}})

        client.force_authenticate(user=None)

    def test_recover(self):
        Account.objects.create(email='mail@rafaelferreira.pt', username='test1', first_name='unit',
                               last_name='test1',
                               teaching_institution='testUA')

        client = APIClient()
        user = Account.objects.get(email='mail@rafaelferreira.pt')
        client.force_authenticate(user=user)

        # recover
        url = "/api/v1/password_recover/request/"
        data = {"email": "mail@rafaelferreira.pt"}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {"email":"mail@rafaelferreira.pt"})

        client.force_authenticate(user=None)