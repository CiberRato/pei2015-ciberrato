from django.test import TestCase
from authentication.models import Account
from rest_framework.test import APIClient


class StatisticsTestCase(TestCase):
    def setUp(self):
        Account.objects.create(email='test@test.com', username='test', first_name='unit', last_name='test',
                               is_staff=True, teaching_institution='testUA')

    def test_results(self):
        user = Account.objects.get(email='test@test.com')
        client = APIClient()
        client.force_authenticate(user=user)

        # media sizes
        url = "/api/v1/statistics/media/"
        response = client.get(path=url)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.status_code, 200)

        client.force_authenticate(user=None)