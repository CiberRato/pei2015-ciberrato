from django.test import TestCase
from authentication.models import Account

from rest_framework.test import APIClient
from collections import OrderedDict

class AuthenticationTestCase(TestCase):
    def setUp(self):
        pass

    def test_uploadFile(self):
        client = APIClient()
        url = "/api/v1/competitions/grid/"
        f = open('/Users/gipmon/Documents/Development/pei2015-ciberonline/src/web/media/tmp_simulations/Ciber2010_Grid.xml', 'r')
        response = client.post(url, {'file': f})
        print response
