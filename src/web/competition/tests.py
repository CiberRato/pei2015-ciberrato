from django.test import TestCase
from competition.models import *

from rest_framework.test import APIClient

class AuthenticationTestCase(TestCase):
    def setUp(self):
        c = Competition.objects.create(name="C1", type_of_competition=Competition.COLABORATIVA)
        r = Round.objects.create(name="R1", parent_competition=c)
        a1 = Account.objects.create(email="rf@rf.pt", username="gipmon", first_name="Rafael", last_name="Ferreira",
                                    teaching_institution="Universidade de Aveiro", is_admin=True)

    def test_uploadFile(self):
        user = Account.objects.get(username="gipmon")
        client = APIClient()
        client.force_authenticate(user=user)

        url = "/api/v1/competitions/round/upload/param_list/?round=R1"
        f = open('/Users/gipmon/Documents/Development/pei2015-ciberonline/src/web/media/tmp_simulations/Param.xml', 'r')
        response = client.post(url, {'file': f})
        print response.data

        url = "/api/v1/competitions/round/upload/grid/?round=R1"
        f = open('/Users/gipmon/Documents/Development/pei2015-ciberonline/src/web/media/tmp_simulations/Ciber2010_Grid.xml', 'r')
        response = client.post(url, {'file': f})
        print response.data

        url = "/api/v1/competitions/round/upload/lab/?round=R1"
        f = open('/Users/gipmon/Documents/Development/pei2015-ciberonline/src/web/media/tmp_simulations/Ciber2010_Lab.xml', 'r')
        response = client.post(url, {'file': f})
        print response.data

        url = "/api/v1/competitions/round/"
        response = client.get(url)
        print response.data

        client.force_authenticate(user=None)
