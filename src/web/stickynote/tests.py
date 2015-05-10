from django.test import TestCase
from authentication.models import Account
from rest_framework.test import APIClient


class AuthenticationTestCase(TestCase):
    def setUp(self):
        Account.objects.create(email='test@test.com', username='test', first_name='unit', last_name='test',
                               is_staff=True, teaching_institution='testUA')

    def test_sticky_note(self):
        user = Account.objects.get(email='test@test.com')
        client = APIClient()
        client.force_authenticate(user=user)

        url = "/api/v1/sticky_notes/crud/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

        url = "/api/v1/sticky_notes/crud/"
        data = {'time': 4, 'note': 'This is a sticky note!'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        rsp = response.data
        identifier = rsp['identifier']
        del rsp['identifier']
        del rsp['created_at']
        del rsp['updated_at']
        self.assertEqual(rsp, {'note': u'This is a sticky note!', 'time': 4, 'active': True})

        url = "/api/v1/sticky_notes/crud/" + identifier + "/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        rsp = response.data
        del rsp['identifier']
        del rsp['created_at']
        del rsp['updated_at']
        self.assertEqual(rsp, {'note': u'This is a sticky note!', 'time': 4, 'active': True})

        url = "/api/v1/sticky_notes/crud/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = response.data
        del rsp[0]['identifier']
        del rsp[0]['created_at']
        del rsp[0]['updated_at']
        self.assertEqual(rsp, [{'note': u'This is a sticky note!', 'time': 4, 'active': True}])

        url = "/api/v1/sticky_notes/crud/" + identifier + "/"
        data = {'note': 'modified note', 'time': 6}
        response = client.put(path=url, data=data)
        self.assertEqual(response.status_code, 200)
        rsp = response.data
        del rsp['identifier']
        del rsp['created_at']
        del rsp['updated_at']
        self.assertEqual(rsp, {'note': u'modified note', 'time': 6, 'active': True})

        url = "/api/v1/sticky_notes/crud/" + identifier + "/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        rsp = response.data
        del rsp['identifier']
        del rsp['created_at']
        del rsp['updated_at']
        self.assertEqual(rsp, {'note': u'modified note', 'time': 6, 'active': True})

        url = "/api/v1/sticky_notes/toggle/"
        data = {'identifier': identifier}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "OK", "message": "The sticky note is now False!"})

        url = "/api/v1/sticky_notes/crud/" + identifier + "/"
        response = client.delete(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "Deleted", "message": "The sticky note has been deleted"})

        url = "/api/v1/sticky_notes/crud/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

        client.force_authenticate(user=None)