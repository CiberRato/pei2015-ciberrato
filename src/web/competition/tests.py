from django.test import TestCase
from competition.models import *
from authentication.models import GroupMember

from rest_framework.test import APIClient
from collections import OrderedDict


class AuthenticationTestCase(TestCase):
    def setUp(self):
        g1 = Group.objects.create(name="XPTO1", max_members=10)
        g2 = Group.objects.create(name="XPTO2", max_members=10)
        g3 = Group.objects.create(name="XPTO3", max_members=10)

        c = Competition.objects.create(name="C1", type_of_competition=settings.COLABORATIVA)
        r = Round.objects.create(name="R1", parent_competition=c)

        a1 = Account.objects.create(email="rf@rf.pt", username="gipmon", first_name="Rafael", last_name="Ferreira",
                                    teaching_institution="Universidade de Aveiro", is_admin=True)
        a2 = Account.objects.create(email="ey@rf.pt", username="eypo", first_name="Costa", last_name="Ferreira",
                                    teaching_institution="Universidade de Aveiro")
        a3 = Account.objects.create(email="af@rf.pt", username="eypo94", first_name="Antonio", last_name="Ferreira",
                                    teaching_institution="Universidade de Aveiro")

        GroupMember.objects.create(account=a1, group=g1, is_admin=True)

        GroupMember.objects.create(account=a2, group=g2, is_admin=True)
        GroupMember.objects.create(account=a1, group=g2, is_admin=True)

        GroupMember.objects.create(account=a3, group=g3, is_admin=True)
        GroupMember.objects.create(account=a1, group=g3, is_admin=True)

    def test_enrollGroup(self):
        user = Account.objects.get(username="gipmon")
        client = APIClient()
        client.force_authenticate(user=user)

        url = "/api/v1/competitions/enroll/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO1'}
        response = client.post(path=url, data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Created', 'message': 'The group has enrolled.'})

        url = "/api/v1/competitions/enroll/"
        response = client.get(path=url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('competition_name', u'C1'), ('group_name', u'XPTO1')])])

        url = "/api/v1/competitions/enroll/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO1'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'status': 'Bad request', 'message': 'The group already enrolled.'})

        url = "/api/v1/competitions/enroll/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO2'}
        response = client.post(path=url, data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Created', 'message': 'The group has enrolled.'})

        url = "/api/v1/competitions/enroll/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO3'}
        response = client.post(path=url, data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Created', 'message': 'The group has enrolled.'})

        url = "/api/v1/competitions/enroll/"
        response = client.get(path=url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('competition_name', u'C1'), ('group_name', u'XPTO1')]),
                                         OrderedDict([('competition_name', u'C1'), ('group_name', u'XPTO2')]),
                                         OrderedDict([('competition_name', u'C1'), ('group_name', u'XPTO3')])])

        # update a group to a valid inscription
        url = "/api/v1/competitions/group_valid/XPTO3/?competition_name=C1"
        response = client.put(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         {"status": "Updated", "message": "The group inscription has been updated to True ."})

        # list of all groups enrolled and with inscriptions valid in one competition
        url = "/api/v1/competitions/groups/C1/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('name', u'XPTO3'), ('max_members', 10)])])

        # list of all groups enrolled and with inscriptions not valid in one competition
        url = "/api/v1/competitions/groups_not_valid/C1/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('name', u'XPTO1'), ('max_members', 10)]),
                                         OrderedDict([('name', u'XPTO2'), ('max_members', 10)])])

        url = "/api/v1/competitions/group_valid/XPTO3/?competition_name=C1"
        response = client.put(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         {"status": "Updated", "message": "The group inscription has been updated to False ."})

        # list of all groups enrolled and with inscriptions not valid in one competition
        url = "/api/v1/competitions/groups_not_valid/C1/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('name', u'XPTO1'), ('max_members', 10)]),
                                         OrderedDict([('name', u'XPTO2'), ('max_members', 10)]),
                                         OrderedDict([('name', u'XPTO3'), ('max_members', 10)])])

        # list of all groups enrolled and with inscriptions valid in one competition
        url = "/api/v1/competitions/groups/C1/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

        url = "/api/v1/competitions/enroll/C1/?group_name=XPTO3"
        response = client.delete(path=url)
        self.assertEqual(response.status_code, 200)

        url = "/api/v1/competitions/enroll/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO3'}
        response = client.post(path=url, data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Created', 'message': 'The group has enrolled.'})

        # create a agent for group
        url = "/api/v1/competitions/agent/"
        data = {'agent_name': 'KAMIKAZE', 'group_name': 'XPTO3'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {"agent_name": "KAMIKAZE", "group_name": "XPTO3"})

        # get the agent information
        url = "/api/v1/competitions/agent/KAMIKAZE/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)

        rsp = dict(response.data)
        del rsp['created_at']
        del rsp['updated_at']

        self.assertEqual(rsp, {'agent_name': u'KAMIKAZE', 'group_name': u'XPTO3', 'user': OrderedDict(
            [('id', 1), ('email', u'rf@rf.pt'), ('username', u'gipmon'),
             ('teaching_institution', u'Universidade de Aveiro'), ('first_name', u'Rafael'),
             ('last_name', u'Ferreira')])})


        # upload agent code
        url = "/api/v1/competitions/upload/agent/?agent_name=KAMIKAZE"
        f = open('/Users/gipmon/Documents/Development/pei2015-ciberonline/src/web/media/tmp_simulations/myrob.py', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'File uploaded!', 'message': 'The agent code has been uploaded!'})

        # delete uploaded file
        url = "/api/v1/competitions/delete_agent_file/KAMIKAZE/?file_name=myrob.py"
        response = client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "Deleted", "message": "The agent file has been deleted"})

        url = "/api/v1/competitions/upload/agent/?agent_name=KAMIKAZE"
        f = open('/Users/gipmon/Documents/Development/pei2015-ciberonline/src/web/media/tmp_simulations/main.c', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'File uploaded!', 'message': 'The agent code has been uploaded!'})

        url = "/api/v1/competitions/upload/agent/?agent_name=KAMIKAZE"
        f = open('/Users/gipmon/Documents/Development/pei2015-ciberonline/src/web/media/tmp_simulations/main.cpp', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'status': 'Bad request', 'message': u'You can only upload files of the same type! Expected: .c'})

        url = "/api/v1/competitions/upload/agent/?agent_name=KAMIKAZE"
        f = open('/Users/gipmon/Documents/Development/pei2015-ciberonline/src/web/media/tmp_simulations/main.java', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'status': 'Bad request', 'message': u'You can only upload files of the same type! Expected: .c'})

        # make the code valid
        agent = Agent.objects.get(agent_name='KAMIKAZE')
        agent.code_valid = True
        agent.save()

        # associate the agent to the competition
        url = "/api/v1/competitions/associate_agent/"
        data = {'round_name': 'R1', 'agent_name': 'KAMIKAZE'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(dict(response.data), {'round_name': u'R1', 'agent_name': u'KAMIKAZE'})
        self.assertEqual(len(CompetitionAgent.objects.filter(agent=agent)), 1)

        # deassociate the agent to the competition
        url = "/api/v1/competitions/associate_agent/KAMIKAZE/?round_name=R1"
        response = client.delete(url)
        self.assertEqual(response.status_code, response.status_code)
        self.assertEqual(response.data, {'status': 'Deleted', 'message': 'The competition agent has been deleted!'})
        self.assertEqual(len(CompetitionAgent.objects.filter(agent=agent)), 0)

        # destroy the agent
        url = "/api/v1/competitions/agent/KAMIKAZE/"
        response = client.delete(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "Deleted", "message": "The agent has been deleted"})

        url = "/api/v1/competitions/agent/KAMIKAZE/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {"detail": "Not found"})

        url = "/api/v1/competitions/enroll/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('competition_name', u'C1'), ('group_name', u'XPTO1')]),
                                         OrderedDict([('competition_name', u'C1'), ('group_name', u'XPTO2')]),
                                         OrderedDict([('competition_name', u'C1'), ('group_name', u'XPTO3')])])

        c = Competition.objects.get(name="C1")
        Round.objects.create(name="R2", parent_competition=c)
        Round.objects.create(name="R3", parent_competition=c)

        # verify get the first competition round
        url = "/api/v1/competitions/earliest_round/C1/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'grid_path': None, 'name': u'R1', 'agents_list': [], 'param_list_path': None,
                                         'lab_path': None, 'parent_competition_name': u'C1'})

        # verify get the first competition round
        url = "/api/v1/competitions/oldest_round/C1/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'grid_path': None, 'name': u'R3', 'agents_list': [], 'param_list_path': None,
                                         'lab_path': None, 'parent_competition_name': u'C1'})

        r3 = Round.objects.get(name="R3")
        r3.delete()

        r2 = Round.objects.get(name="R2")
        r2.delete()

        url = "/api/v1/competitions/round/R1/"
        response = client.delete(url)
        self.assertEqual(response.status_code, 200)

        url = "/api/v1/competitions/round/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

        client.force_authenticate(user=None)

    # def test_remove_competiton recursive removeall

    def test_uploadFile(self):
        user = Account.objects.get(username="gipmon")
        client = APIClient()
        client.force_authenticate(user=user)

        url = "/api/v1/competitions/round/upload/param_list/?round=R1"
        f = open('/Users/gipmon/Documents/Development/pei2015-ciberonline/src/web/media/tmp_simulations/Param.xml', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Uploaded', 'message': 'The file has been uploaded and saved to R1'})

        url = "/api/v1/competitions/round/upload/grid/?round=R1"
        f = open(
            '/Users/gipmon/Documents/Development/pei2015-ciberonline/src/web/media/tmp_simulations/Ciber2010_Grid.xml',
            'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Uploaded', 'message': 'The file has been uploaded and saved to R1'})

        url = "/api/v1/competitions/round/upload/lab/?round=R1"
        f = open(
            '/Users/gipmon/Documents/Development/pei2015-ciberonline/src/web/media/tmp_simulations/Ciber2010_Lab.xml',
            'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Uploaded', 'message': 'The file has been uploaded and saved to R1'})

        url = "/api/v1/competitions/round/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        # print response.data
        # self.assertEqual(response.data, [OrderedDict([('name', u'R1'), ('parent_competition_name', u'C1'), ('param_list_path', '/media/competition_files/param_list/Param_D7V8vSV.xml'), ('grid_path', '/media/competition_files/grid/Ciber2010_Grid_sMNbKrC.xml'), ('lab_path', '/media/competition_files/lab/Ciber2010_Lab_OjaD24i.xml'), ('agents_list', [])])])

        for r in Round.objects.all():
            r.lab_path.delete()
            r.param_list_path.delete()
            r.grid_path.delete()

        url = "/api/v1/competitions/round/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict(
            [('name', u'R1'), ('parent_competition_name', u'C1'), ('param_list_path', None), ('grid_path', None),
             ('lab_path', None), ('agents_list', [])])])

        client.force_authenticate(user=None)
