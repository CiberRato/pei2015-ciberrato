from collections import OrderedDict

from django.test import TestCase
from competition.models import *
from authentication.models import TeamMember
from rest_framework.test import APIClient


class AuthenticationTestCase(TestCase):
    def setUp(self):
        g1 = Team.objects.create(name="XPTO1", max_members=10)
        g2 = Team.objects.create(name="XPTO2", max_members=10)

        a1 = Account.objects.create(email="rf@rf.pt", username="gipmon", first_name="Rafael", last_name="Ferreira",
                                    teaching_institution="Universidade de Aveiro", is_staff=True)
        a2 = Account.objects.create(email="ey@rf.pt", username="eypo", first_name="Costa", last_name="Ferreira",
                                    teaching_institution="Universidade de Aveiro")

        TeamMember.objects.create(account=a1, team=g1, is_admin=True)
        TeamMember.objects.create(account=a2, team=g2, is_admin=True)

    def test_agentPermissions(self):
        # agent.py
        user = Account.objects.get(username="gipmon")
        client = APIClient()
        client.force_authenticate(user=user)

        # create a agent for team, without code first
        url = "/api/v1/agents/agent/"
        data = {'agent_name': 'KAMIKAZE', 'team_name': 'XPTO1', 'language': 'Python'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict(
            [(u'agent_name', u'KAMIKAZE'), (u'language', 'Python'), (u'team_name', u'XPTO1')]))

        # create a agent for team, without code first
        url = "/api/v1/agents/agent/"
        data = {'agent_name': 'KAMIKAZE', 'team_name': 'XPTO2', 'language': 'Python'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {"detail": "You do not have permission to perform this action."})

        user = Account.objects.get(username="eypo")
        client2 = APIClient()
        client2.force_authenticate(user=user)

        url = "/api/v1/agents/agent/KAMIKAZE/?team_name=XPTO1"
        response = client2.get(path=url)
        self.assertEqual(response.data, {"detail": "You must be part of the team."})
        self.assertEqual(response.status_code, 403)

        url = "/api/v1/agents/agent/KAMIKAZE/?team_name=XPTO1"
        response = client2.delete(path=url)
        self.assertEqual(response.data, {u'detail': u'You do not have permission to perform this action.'})
        self.assertEqual(response.status_code, 403)

        url = "/api/v1/agents/validate_code/"
        data = {'agent_name': 'KAMIKAZE', 'team_name': 'XPTO1'}
        response = client2.post(path=url, data=data)
        self.assertEqual(response.data, {"detail": "You must be part of the team."})
        self.assertEqual(response.status_code, 403)

        # now with the team member must be possible to do
        url = "/api/v1/agents/agent/KAMIKAZE/?team_name=XPTO1"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)

        url = "/api/v1/agents/agent/KAMIKAZE/?team_name=XPTO1"
        response = client.delete(path=url)
        self.assertEqual(response.data, {"status": "Deleted", "message": "The agent has been deleted"})
        self.assertEqual(Agent.objects.all().count(), 0)

        client.force_authenticate(user=None)
        client2.force_authenticate(user=None)