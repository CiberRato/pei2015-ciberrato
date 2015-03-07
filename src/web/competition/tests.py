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
        data = {'agent_name': 'KAMIKAZE', 'group_name': 'XPTO3', 'is_virtual': False}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict(
            [('agent_name', u'KAMIKAZE'), ('is_virtual', False), ('rounds', []), ('competitions', []),
             ('group_name', u'XPTO3')]))

        # get the agent information
        url = "/api/v1/competitions/agent/KAMIKAZE/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)

        rsp = dict(response.data)
        del rsp['created_at']
        del rsp['updated_at']

        self.assertEqual(rsp, {'agent_name': u'KAMIKAZE', 'competitions': [], 'is_virtual': False, 'language': u'',
                               'rounds': [], 'group_name': u'XPTO3',
                               'user': OrderedDict(
                                   [('id', 1), ('email', u'rf@rf.pt'), ('username', u'gipmon'),
                                    ('teaching_institution', u'Universidade de Aveiro'), ('first_name', u'Rafael'),
                                    ('last_name', u'Ferreira')])})


        # upload agent code
        url = "/api/v1/competitions/upload/agent/?agent_name=KAMIKAZE&language=Python"
        f = open('/Users/gipmon/Documents/Development/pei2015-ciberonline/src/web/media/tmp_simulations/myrob.py', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'File uploaded!', 'message': 'The agent code has been uploaded!'})

        # delete uploaded file
        url = "/api/v1/competitions/delete_agent_file/KAMIKAZE/?file_name=myrob.py"
        response = client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "Deleted", "message": "The agent file has been deleted"})

        url = "/api/v1/competitions/upload/agent/?agent_name=KAMIKAZE&language=C"
        f = open('/Users/gipmon/Documents/Development/pei2015-ciberonline/src/web/media/tmp_simulations/main.c', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'File uploaded!', 'message': 'The agent code has been uploaded!'})

        url = "/api/v1/competitions/upload/agent/?agent_name=KAMIKAZE&language=cplusplus"
        f = open('/Users/gipmon/Documents/Development/pei2015-ciberonline/src/web/media/tmp_simulations/main.cpp', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'File uploaded!', 'message': 'The agent code has been uploaded!'})

        url = "/api/v1/competitions/upload/agent/?agent_name=KAMIKAZE&language=Java"
        f = open('/Users/gipmon/Documents/Development/pei2015-ciberonline/src/web/media/tmp_simulations/main.java', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'File uploaded!', 'message': 'The agent code has been uploaded!'})

        url = "/api/v1/competitions/agent/KAMIKAZE/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = dict(response.data)
        del rsp['created_at']
        del rsp['updated_at']
        self.assertEqual(rsp, {'agent_name': u'KAMIKAZE', 'rounds': [], 'competitions': [], 'user': OrderedDict(
            [('id', 1), ('email', u'rf@rf.pt'), ('username', u'gipmon'),
             ('teaching_institution', u'Universidade de Aveiro'), ('first_name', u'Rafael'),
             ('last_name', u'Ferreira')]), 'language': 'Java', 'is_virtual': False,
                               'group_name': u'XPTO3'})

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

        url = "/api/v1/competitions/agent/KAMIKAZE/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = dict(response.data)
        del rsp['created_at']
        del rsp['updated_at']
        self.assertEqual(rsp, {'agent_name': u'KAMIKAZE', 'rounds': [OrderedDict(
            [('name', u'R1'), ('parent_competition_name', u'C1'), ('param_list_path', None), ('grid_path', None),
             ('lab_path', None), ('agents_list', [1])])], 'competitions': [
            OrderedDict([('name', u'C1'), ('type_of_competition', 'CB'), ('enrolled_groups', [1, 2, 3])])],
                               'user': OrderedDict(
                                   [('id', 1), ('email', u'rf@rf.pt'), ('username', u'gipmon'),
                                    ('teaching_institution', u'Universidade de Aveiro'), ('first_name', u'Rafael'),
                                    ('last_name', u'Ferreira')]), 'language': 'Java', 'is_virtual': False,
                               'group_name': u'XPTO3'})

        # retrieve the agent list of one round
        url = "/api/v1/competitions/valid_round_agents/R1/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = response.data
        del rsp[0]['created_at']
        del rsp[0]['updated_at']
        self.assertEqual(rsp, [OrderedDict([('round_name', u'R1'), ('agent_name', u'KAMIKAZE')])])

        # test participants for one round
        url = "/api/v1/competitions/valid_round_participants/R1/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('id', 3), ('email', u'af@rf.pt'), ('username', u'eypo94'),
                                                      ('teaching_institution', u'Universidade de Aveiro'),
                                                      ('first_name', u'Antonio'), ('last_name', u'Ferreira')]),
                                         OrderedDict([('id', 1), ('email', u'rf@rf.pt'), ('username', u'gipmon'),
                                                      ('teaching_institution', u'Universidade de Aveiro'),
                                                      ('first_name', u'Rafael'), ('last_name', u'Ferreira')])])

        # test groups for one round
        url = "/api/v1/competitions/valid_round_groups/R1/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('name', u'XPTO3'), ('max_members', 10)])])

        r = Round.objects.get(name="R1")
        competition_agent = CompetitionAgent.objects.filter(round=r)
        competition_agent = competition_agent[0]
        competition_agent.eligible = False
        competition_agent.save()

        # retrieve the not eligible agents for one round
        url = "/api/v1/competitions/not_eligible_round_agents/R1/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = response.data
        del rsp[0]['created_at']
        del rsp[0]['updated_at']
        self.assertEqual(rsp, [OrderedDict([('round_name', u'R1'), ('agent_name', u'KAMIKAZE')])])

        # retrieve the not eligible participantes for one round
        url = "/api/v1/competitions/not_eligible_round_participants/R1/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('id', 3), ('email', u'af@rf.pt'), ('username', u'eypo94'),
                                                      ('teaching_institution', u'Universidade de Aveiro'),
                                                      ('first_name', u'Antonio'), ('last_name', u'Ferreira')]),
                                         OrderedDict([('id', 1), ('email', u'rf@rf.pt'), ('username', u'gipmon'),
                                                      ('teaching_institution', u'Universidade de Aveiro'),
                                                      ('first_name', u'Rafael'), ('last_name', u'Ferreira')])])

        # test not eligible groups for one round
        url = "/api/v1/competitions/not_eligible_round_groups/R1/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('name', u'XPTO3'), ('max_members', 10)])])

        # create simulation
        url = "/api/v1/competitions/simulation/"
        data = {'round_name': 'R1'}
        response = client.post(path=url, data=data)
        rsp = dict(response.data)
        del rsp['created_at']
        del rsp['updated_at']
        identifier = rsp['identifier']
        del rsp['identifier']
        self.assertEqual(rsp, {'round_name': u'R1'})
        self.assertEqual(response.status_code, 201)

        # retrieve the simulation data
        url = "/api/v1/competitions/simulation/" + identifier + "/"
        response = client.get(url)
        rsp = dict(response.data)
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['identifier']
        self.assertEqual(rsp, {'round_name': u'R1'})
        self.assertEqual(response.status_code, 200)

        # associate an agent to the simulation
        url = "/api/v1/competitions/associate_agent_to_simulation/"
        data = {'round_name': 'R1', 'simulation_identifier': identifier, 'agent_name': 'KAMIKAZE', 'pos': 1}
        response = client.post(path=url, data=data)
        self.assertEqual(dict(response.data),
                         {'round_name': u'R1', 'agent_name': u'KAMIKAZE', 'pos': 1,
                          'simulation_identifier': identifier})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(LogSimulationAgent.objects.all()), 1)

        # get the simulations by agent
        url = "/api/v1/competitions/simulations_by_agent/KAMIKAZE/"
        response = client.get(url)
        rsp = response.data[0]
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['identifier']
        self.assertEqual(rsp, {'round_name': u'R1'})
        self.assertEqual(response.status_code, 200)

        # get the simulations by round
        url = "/api/v1/competitions/simulations_by_round/R1/"
        response = client.get(url)
        rsp = response.data[0]
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['identifier']
        self.assertEqual(rsp, {'round_name': u'R1'})
        self.assertEqual(response.status_code, 200)

        # get the simulations by competition
        url = "/api/v1/competitions/simulations_by_competition/C1/"
        response = client.get(url)
        rsp = response.data[0]
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['identifier']
        self.assertEqual(rsp, {'round_name': u'R1'})
        self.assertEqual(response.status_code, 200)

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

        # get simulation for simulate
        url = "/api/v1/competitions/get_simulations/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = response.data[0]
        del rsp['simulation_id']
        del rsp['agents']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(rsp, {'param_list': u'/api/v1/competitions/round_file/R1/?file=param_list', 'grid': u'/api/v1/competitions/round_file/R1/?file=grid', 'lab': u'/api/v1/competitions/round_file/R1/?file=lab'})

        # get round file: param_list
        url = "/api/v1/competitions/round_file/R1/?file=param_list"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        # get round file: grid
        url = "/api/v1/competitions/round_file/R1/?file=grid"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        # get round file: lab
        url = "/api/v1/competitions/round_file/R1/?file=lab"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        # get the agent files
        url = "/api/v1/competitions/agent_file/"+identifier+"/KAMIKAZE/"
        response = client.get(url)
        print response

        for r in Round.objects.all():
            r.lab_path.delete()
            r.param_list_path.delete()
            r.grid_path.delete()

        # deassociate the agent to the competition
        url = "/api/v1/competitions/associate_agent/KAMIKAZE/?round_name=R1"
        response = client.delete(url)
        self.assertEqual(response.status_code, response.status_code)
        self.assertEqual(response.data, {'status': 'Deleted', 'message': 'The competition agent has been deleted!'})
        self.assertEqual(len(CompetitionAgent.objects.filter(agent=agent)), 0)

        # delete the simulation data
        url = "/api/v1/competitions/simulation/" + identifier + "/"
        response = client.delete(url)
        self.assertEqual(response.data, {'status': 'Deleted', 'message': 'The simulation has been deleted'})
        self.assertEqual(response.status_code, 200)

        # retrieve the simulation data
        url = "/api/v1/competitions/simulation/" + identifier + "/"
        response = client.get(url)
        self.assertEqual(response.data, {u'detail': u'Not found'})

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

        url = "/api/v1/competitions/round/R1/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

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
