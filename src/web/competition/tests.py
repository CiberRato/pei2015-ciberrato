from django.test import TestCase
from competition.models import *
from authentication.models import GroupMember

from rest_framework.test import APIClient
from collections import OrderedDict
import json


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

        # create competition
        url = "/api/v1/competitions/crud/"
        data = {'name': 'C2', 'type_of_competition': settings.COMPETITIVA}
        response = client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict([('name', u'C2'), ('type_of_competition', settings.COMPETITIVA)]))

        # get competition Register
        url = "/api/v1/competitions/get/Register/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         [{"name": "C1", "type_of_competition": "Collaborative", "state_of_competition": "Register"},
                          {"name": "C2", "type_of_competition": "Competitive", "state_of_competition": "Register"}])

        # get all competitions
        url = "/api/v1/competitions/get/All/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         [{"name": "C1", "type_of_competition": "Collaborative", "state_of_competition": "Register"},
                          {"name": "C2", "type_of_competition": "Competitive", "state_of_competition": "Register"}])

        # enroll one group in the competition, the group stays with the inscription valid=False
        url = "/api/v1/competitions/enroll/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO1'}
        response = client.post(path=url, data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Created', 'message': 'The group has enrolled.'})

        # groups that enrolled in the competition
        url = "/api/v1/competitions/enroll/"
        response = client.get(path=url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         [OrderedDict([('competition_name', u'C1'), ('group_name', u'XPTO1'), ('valid', False)])])

        # the group can't enroll twice
        url = "/api/v1/competitions/enroll/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO1'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'status': 'Bad request', 'message': 'The group already enrolled.'})

        # enroll another group to the competition
        url = "/api/v1/competitions/enroll/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO2'}
        response = client.post(path=url, data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Created', 'message': 'The group has enrolled.'})

        # and another one :D
        url = "/api/v1/competitions/enroll/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO3'}
        response = client.post(path=url, data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Created', 'message': 'The group has enrolled.'})

        # see who are in the competition!
        url = "/api/v1/competitions/enroll/"
        response = client.get(path=url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         [OrderedDict([('competition_name', u'C1'), ('group_name', u'XPTO1'), ('valid', False)]),
                          OrderedDict([('competition_name', u'C1'), ('group_name', u'XPTO2'), ('valid', False)]),
                          OrderedDict([('competition_name', u'C1'), ('group_name', u'XPTO3'), ('valid', False)])])

        # only admin
        url = "/api/v1/competitions/toggle_group_inscription/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO3'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'status': 'Inscription toggled!', 'message': 'Inscription is now: True'})
        self.assertEqual(response.status_code, 200)

        # list of all groups enrolled and with inscriptions valid or not in one competition
        url = "/api/v1/competitions/groups/C1/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [
            OrderedDict([('group', OrderedDict([('name', u'XPTO1'), ('max_members', 10)])), ('valid', False)]),
            OrderedDict([('group', OrderedDict([('name', u'XPTO2'), ('max_members', 10)])), ('valid', False)]),
            OrderedDict([('group', OrderedDict([('name', u'XPTO3'), ('max_members', 10)])), ('valid', True)])])

        # list of all groups enrolled and with inscriptions not valid in one competition
        url = "/api/v1/competitions/groups_not_valid/C1/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('name', u'XPTO1'), ('max_members', 10)]),
                                         OrderedDict([('name', u'XPTO2'), ('max_members', 10)])])

        # only admin
        url = "/api/v1/competitions/toggle_group_inscription/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO3'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'status': 'Inscription toggled!', 'message': 'Inscription is now: False'})
        self.assertEqual(response.status_code, 200)

        # list of all groups enrolled and with inscriptions not valid in one competition
        url = "/api/v1/competitions/groups_not_valid/C1/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('name', u'XPTO1'), ('max_members', 10)]),
                                         OrderedDict([('name', u'XPTO2'), ('max_members', 10)]),
                                         OrderedDict([('name', u'XPTO3'), ('max_members', 10)])])

        # list of all groups enrolled and with inscriptions valid or not in one competition
        url = "/api/v1/competitions/groups/C1/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [
            OrderedDict([('group', OrderedDict([('name', u'XPTO1'), ('max_members', 10)])), ('valid', False)]),
            OrderedDict([('group', OrderedDict([('name', u'XPTO2'), ('max_members', 10)])), ('valid', False)]),
            OrderedDict([('group', OrderedDict([('name', u'XPTO3'), ('max_members', 10)])), ('valid', False)])])

        # delete the group enroll from the competition
        url = "/api/v1/competitions/enroll/C1/?group_name=XPTO3"
        response = client.delete(path=url)
        self.assertEqual(response.status_code, 200)

        # enroll the group again, and OK
        url = "/api/v1/competitions/enroll/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO3'}
        response = client.post(path=url, data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Created', 'message': 'The group has enrolled.'})

        # create a agent for group, without code first
        url = "/api/v1/competitions/agent/"
        data = {'agent_name': 'KAMIKAZE', 'group_name': 'XPTO3', 'is_virtual': False}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data,
                         OrderedDict([('agent_name', u'KAMIKAZE'), ('is_virtual', False), ('group_name', u'XPTO3')]))

        # get agents by group
        url = "/api/v1/competitions/agents_by_group/XPTO3/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = response.data[0]
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['user']['updated_at']
        del rsp['user']['created_at']

        self.assertEqual(rsp, OrderedDict(
            [('agent_name', u'KAMIKAZE'), ('is_virtual', False), ('language', u''), ('rounds', []),
             ('competitions', []), ('user', OrderedDict([('email', u'rf@rf.pt'), ('username', u'gipmon'),
                                                         ('teaching_institution', u'Universidade de Aveiro'),
                                                         ('first_name', u'Rafael'), ('last_name', u'Ferreira')])),
             ('group_name', u'XPTO3')]))

        # get agents by user
        url = "/api/v1/competitions/agents_by_user/gipmon/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = response.data[0]
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['user']['updated_at']
        del rsp['user']['created_at']

        self.assertEqual(rsp, OrderedDict(
            [('agent_name', u'KAMIKAZE'), ('is_virtual', False), ('language', u''), ('rounds', []),
             ('competitions', []), ('user', OrderedDict([('email', u'rf@rf.pt'), ('username', u'gipmon'),
                                                         ('teaching_institution', u'Universidade de Aveiro'),
                                                         ('first_name', u'Rafael'), ('last_name', u'Ferreira')])),
             ('group_name', u'XPTO3')]))

        # get the agent information about the agent
        url = "/api/v1/competitions/agent/KAMIKAZE/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)

        rsp = dict(response.data)
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['user']['updated_at']
        del rsp['user']['created_at']

        self.assertEqual(rsp, {'agent_name': u'KAMIKAZE', 'competitions': [], 'is_virtual': False, 'language': u'',
                               'rounds': [], 'group_name': u'XPTO3',
                               'user': OrderedDict(
                                   [('email', u'rf@rf.pt'), ('username', u'gipmon'),
                                    ('teaching_institution', u'Universidade de Aveiro'), ('first_name', u'Rafael'),
                                    ('last_name', u'Ferreira')])})


        # upload agent code
        url = "/api/v1/competitions/upload/agent/?agent_name=KAMIKAZE&language=Python"
        f = open('media/tests_files/myrob_do.py', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'File uploaded!', 'message': 'The agent code has been uploaded!'})

        # delete uploaded file
        url = "/api/v1/competitions/delete_agent_file/KAMIKAZE/?file_name=myrob_do.py"
        response = client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "Deleted", "message": "The agent file has been deleted"})

        url = "/api/v1/competitions/upload/agent/?agent_name=KAMIKAZE&language=C"
        f = open('media/tests_files/main.c', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'File uploaded!', 'message': 'The agent code has been uploaded!'})

        url = "/api/v1/competitions/upload/agent/?agent_name=KAMIKAZE&language=cplusplus"
        f = open('media/tests_files/main.cpp', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'File uploaded!', 'message': 'The agent code has been uploaded!'})

        url = "/api/v1/competitions/upload/agent/?agent_name=KAMIKAZE&language=Java"
        f = open('media/tests_files/main.java', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'File uploaded!', 'message': 'The agent code has been uploaded!'})

        url = "/api/v1/competitions/agent_files/KAMIKAZE/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

        url = "/api/v1/competitions/agent/KAMIKAZE/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = dict(response.data)
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['user']['updated_at']
        del rsp['user']['created_at']

        self.assertEqual(rsp, {'agent_name': u'KAMIKAZE', 'rounds': [], 'competitions': [], 'user': OrderedDict(
            [('email', u'rf@rf.pt'), ('username', u'gipmon'),
             ('teaching_institution', u'Universidade de Aveiro'), ('first_name', u'Rafael'),
             ('last_name', u'Ferreira')]), 'language': 'Java', 'is_virtual': False,
                               'group_name': u'XPTO3'})

        url = "/api/v1/competitions/allowed_languages/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data),
                         [["Python", "Python"], ["C", "C"], ["C++", "cplusplus"], ["Java", "Java"]])

        # make the code valid, this operation only can be made by the script (server validation)
        agent = Agent.objects.get(agent_name='KAMIKAZE')
        agent.code_valid = True
        agent.save()

        # only admin
        url = "/api/v1/competitions/toggle_group_inscription/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO3'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'status': 'Inscription toggled!', 'message': 'Inscription is now: True'})
        self.assertEqual(response.status_code, 200)

        # associate the agent to the competition
        url = "/api/v1/competitions/associate_agent/"
        data = {'competition_name': 'C1', 'agent_name': 'KAMIKAZE'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(dict(response.data), {'competition_name': u'C1', 'agent_name': u'KAMIKAZE'})
        self.assertEqual(len(CompetitionAgent.objects.filter(agent=agent)), 1)

        # see the information about the agent
        url = "/api/v1/competitions/agent/KAMIKAZE/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = dict(response.data)
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['user']['updated_at']
        del rsp['user']['created_at']

        self.assertEqual(rsp,
                         {'agent_name': u'KAMIKAZE', 'language': 'Java', 'is_virtual': False, 'group_name': u'XPTO3',
                          'competitions': [OrderedDict([('name', u'C1'), ('type_of_competition', settings.COLABORATIVA),
                                                        ('state_of_competition', 'Register')])], 'user': OrderedDict(
                             [('email', u'rf@rf.pt'), ('username', u'gipmon'),
                              ('teaching_institution', u'Universidade de Aveiro'), ('first_name', u'Rafael'),
                              ('last_name', u'Ferreira')]), 'rounds': [OrderedDict([('name', u'R1'),
                                                                                    ('parent_competition_name',
                                                                                     u'C1')])]})

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
        rsp = response.data
        del rsp[0]['created_at']
        del rsp[0]['updated_at']
        del rsp[1]['created_at']
        del rsp[1]['updated_at']

        self.assertEqual(rsp, [OrderedDict([('email', u'af@rf.pt'), ('username', u'eypo94'),
                                            ('teaching_institution', u'Universidade de Aveiro'),
                                            ('first_name', u'Antonio'), ('last_name', u'Ferreira')]),
                               OrderedDict([('email', u'rf@rf.pt'), ('username', u'gipmon'),
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
        rsp = response.data
        del rsp[0]['created_at']
        del rsp[0]['updated_at']
        del rsp[1]['created_at']
        del rsp[1]['updated_at']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('email', u'af@rf.pt'), ('username', u'eypo94'),
                                                      ('teaching_institution', u'Universidade de Aveiro'),
                                                      ('first_name', u'Antonio'), ('last_name', u'Ferreira')]),
                                         OrderedDict([('email', u'rf@rf.pt'), ('username', u'gipmon'),
                                                      ('teaching_institution', u'Universidade de Aveiro'),
                                                      ('first_name', u'Rafael'), ('last_name', u'Ferreira')])])

        # test not eligible groups for one round
        url = "/api/v1/competitions/not_eligible_round_groups/R1/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('name', u'XPTO3'), ('max_members', 10)])])

        # create simulation (only by admin)
        url = "/api/v1/competitions/simulation/"
        data = {'round_name': 'R1'}
        response = client.post(path=url, data=data)
        rsp = dict(response.data)
        del rsp['created_at']
        del rsp['updated_at']
        identifier = rsp['identifier']
        del rsp['identifier']
        self.assertEqual(rsp, {'round_name': u'R1', 'state': u'WAITING'})
        self.assertEqual(response.status_code, 201)

        # retrieve the simulation data
        url = "/api/v1/competitions/simulation/" + identifier + "/"
        response = client.get(url)
        rsp = dict(response.data)
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['identifier']
        self.assertEqual(rsp, {'round_name': u'R1', 'state': u'WAITING'})
        self.assertEqual(response.status_code, 200)

        competition_agent.eligible = True
        competition_agent.save()

        # associate an agent to the simulation (only can be made by an admin)
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
        self.assertEqual(rsp, {'round_name': u'R1', 'state': u'WAITING'})
        self.assertEqual(response.status_code, 200)

        # get the simulations by round
        url = "/api/v1/competitions/simulations_by_round/R1/"
        response = client.get(url)
        rsp = response.data[0]
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['identifier']
        self.assertEqual(rsp, {'round_name': u'R1', 'state': u'WAITING'})
        self.assertEqual(response.status_code, 200)

        # get the simulations by competition
        url = "/api/v1/competitions/simulations_by_competition/C1/"
        response = client.get(url)
        rsp = response.data[0]
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['identifier']
        self.assertEqual(rsp, {'round_name': u'R1', 'state': u'WAITING'})
        self.assertEqual(response.status_code, 200)

        # get the simulation groups
        url = "/api/v1/competitions/simulation_agents/" + identifier + "/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict(
            [('simulation_identifier', u'' + identifier), ('agent_name', u'KAMIKAZE'), ('round_name', u'R1'),
             ('pos', 1)])])

        # only  by admin
        url = "/api/v1/competitions/round/upload/param_list/?round=R1"
        f = open('media/tests_files/Param.xml', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Uploaded', 'message': 'The file has been uploaded and saved to R1'})

        # only  by admin
        url = "/api/v1/competitions/round/upload/grid/?round=R1"
        f = open('media/tests_files/Ciber2010_Grid.xml', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Uploaded', 'message': 'The file has been uploaded and saved to R1'})

        # only  by admin
        url = "/api/v1/competitions/round/upload/lab/?round=R1"
        f = open('media/tests_files/Ciber2010_Lab.xml', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Uploaded', 'message': 'The file has been uploaded and saved to R1'})

        # see if the files were registred
        url = "/api/v1/competitions/round_admin/R1/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        # print dict(response.data) # show the round files
        self.assertEqual(len(dict(response.data)), 5)

        # start simulation
        url = "/api/v1/simulations/start/"
        data = {'simulation_id': identifier}
        response = client.post(path=url, data=data)
        if response.status_code == 200:
            self.assertEqual(response.data, {'status': 'Simulation started',
                                             'message': 'Please wait that the simulation starts at the simulator!'})
        elif response.status_code == 400:
            self.assertEqual(response.data, {'status': 'Bad Request', 'message': 'The simulator appears to be down!'})

        # get simulation for simulate
        url = "/api/v1/competitions/get_simulation/" + identifier + "/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = response.data
        del rsp['simulation_id']
        del rsp['agents']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(rsp, {'param_list': u'/api/v1/competitions/round_file/R1/?file=param_list',
                               'grid': u'/api/v1/competitions/round_file/R1/?file=grid',
                               'lab': u'/api/v1/competitions/round_file/R1/?file=lab'})

        # save simulation logs (only server by server)
        f = open('media/tests_files/ciberOnline_log.json.zip', 'r')
        url = "/api/v1/competitions/simulation_log/"
        data = {'simulation_identifier': identifier, 'log_json': f}
        response = client.post(url, data)
        self.assertEqual(response.data, {'status': 'Created', 'message': 'The log has been uploaded!'})
        self.assertEqual(response.status_code, 201)
        simulation = Simulation.objects.get(identifier=identifier)
        self.assertEqual(simulation.log_json is None, False)

        # get log sent
        url = "/api/v1/competitions/get_simulation_log/" + identifier + "/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        simulation.log_json.delete()

        # delete simulation
        url = "/api/v1/competitions/associate_agent_to_simulation/" + identifier + "/?round_name=R1&agent_name=KAMIKAZE"
        response = client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'status': 'Deleted', 'message': 'The simulation agent has been deleted!'})
        self.assertEqual(len(LogSimulationAgent.objects.all()), 0)

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
        url = "/api/v1/competitions/agent_file/" + identifier + "/KAMIKAZE/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        for r in Round.objects.all():
            r.lab_path.delete()
            r.param_list_path.delete()
            r.grid_path.delete()

        # deassociate the agent to the competition
        url = "/api/v1/competitions/associate_agent/KAMIKAZE/?competition_name=C1"
        response = client.delete(url)
        self.assertEqual(response.status_code, response.status_code)
        self.assertEqual(response.data, {'status': 'Deleted', 'message': 'The competition agent has been deleted!'})
        self.assertEqual(len(CompetitionAgent.objects.filter(agent=agent)), 0)

        # associate agent to round
        url = '/api/v1/competitions/associate_agent_admin/'
        data = {'round_name': 'R1', 'agent_name': 'KAMIKAZE'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, OrderedDict([('round_name', u'R1'), ('agent_name', u'KAMIKAZE')]))
        self.assertEqual(response.status_code, 201)

        # deassociate the agent to the competition
        url = "/api/v1/competitions/associate_agent_admin/KAMIKAZE/"
        data = {'round_name': 'R1'}
        response = client.delete(path=url, data=data)
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
        self.assertEqual(response.data, {u'detail': u'Not found.'})

        # destroy the agent
        url = "/api/v1/competitions/agent/KAMIKAZE/"
        response = client.delete(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "Deleted", "message": "The agent has been deleted"})

        url = "/api/v1/competitions/agent/KAMIKAZE/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {u'detail': u'Not found.'})

        url = "/api/v1/competitions/enroll/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         [OrderedDict([('competition_name', u'C1'), ('group_name', u'XPTO1'), ('valid', False)]),
                          OrderedDict([('competition_name', u'C1'), ('group_name', u'XPTO2'), ('valid', False)]),
                          OrderedDict([('competition_name', u'C1'), ('group_name', u'XPTO3'), ('valid', True)])])

        # get my enrolled groups
        url = "/api/v1/competitions/my_enrolled_groups_competition/gipmon/?competition_name=C1"
        response = client.get(path=url)
        self.assertEqual([OrderedDict([('competition_name', u'C1'), ('group_name', u'XPTO1'), ('valid', False)]),
                          OrderedDict([('competition_name', u'C1'), ('group_name', u'XPTO2'), ('valid', False)]),
                          OrderedDict([('competition_name', u'C1'), ('group_name', u'XPTO3'), ('valid', True)])],
                         response.data)
        self.assertEqual(response.status_code, 200)

        c = Competition.objects.get(name="C1")
        Round.objects.create(name="R2", parent_competition=c)
        Round.objects.create(name="R3", parent_competition=c)

        # get the competition rounds
        url = "/api/v1/competitions/rounds/C1/"
        response = client.get(url)
        self.assertEqual(response.data, [OrderedDict([('name', u'R1'), ('parent_competition_name', u'C1')]),
                                         OrderedDict([('name', u'R2'), ('parent_competition_name', u'C1')]),
                                         OrderedDict([('name', u'R3'), ('parent_competition_name', u'C1')])])
        self.assertEqual(response.status_code, 200)

        # get group enrolled competitions
        url = "/api/v1/competitions/group_enrolled_competitions/XPTO3/"
        response = client.get(url)
        self.assertEqual(response.data, [OrderedDict(
            [('name', u'C1'), ('type_of_competition', 'Collaborative'), ('state_of_competition', 'Register')])])
        self.assertEqual(response.status_code, 200)

        # verify get the first competition round
        url = "/api/v1/competitions/earliest_round/C1/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'name': u'R1', 'parent_competition_name': u'C1'})

        # verify get the first competition round
        url = "/api/v1/competitions/oldest_round/C1/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'name': u'R3', 'parent_competition_name': u'C1'})

        # change competition state
        url = "/api/v1/competitions/state/C1/"
        data = {'state_of_competition': 'Competition'}
        response = client.put(path=url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, OrderedDict([(u'state_of_competition', 'Competition')]))

        # get competition Competition
        url = "/api/v1/competitions/get/Competition/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         [{"name": "C1", "type_of_competition": "Collaborative", "state_of_competition": "Competition"}])

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

    def cascade_setup(self):
        references = []
        # create competition
        c3 = Competition.objects.create(name="C3")
        references += [c3]

        # create round
        r7 = Round.objects.create(name="R7", parent_competition=c3)
        references += [r7]

        # create another round
        r8 = Round.objects.create(name="R8", parent_competition=c3)
        references += [r8]

        # create another round more
        r9 = Round.objects.create(name="R9", parent_competition=c3)
        references += [r9]

        # create an agent
        user = Account.objects.get(username="gipmon")
        group = Group.objects.get(name="XPTO1")
        a = Agent.objects.create(agent_name="RQ7", user=user, group=group)
        references += [a]

        # create a competition agent
        competition_agent = CompetitionAgent.objects.create(competition=c3, round=r7, agent=a)
        references += [competition_agent]

        # enroll in competition
        group_enrolled = GroupEnrolled.objects.create(competition=c3, group=group)
        references += [group_enrolled]

        # create simulation
        simulation = Simulation.objects.create(round=r7)
        references += [simulation]

        # create simulation agent
        lga = LogSimulationAgent.objects.create(competition_agent=competition_agent, simulation=simulation, pos=1)
        references += [lga]

        # c3|r7|r8|r9|a|competition_agent|group_enroll|simulation|lga
        return references

    def test_cascade_delete_competition(self):
        references = self.cascade_setup()

        competition_len = len(Competition.objects.all())  # 2 => C1 and C2
        round_len = len(Round.objects.all())  # 4 => R1, R7, R8 e R9
        agent_len = len(Agent.objects.all())  # 1 => RQ7
        competition_agent_len = len(CompetitionAgent.objects.all())  # 1
        group_enrolled_len = len(GroupEnrolled.objects.all())  # 1
        simulation_len = len(Simulation.objects.all())  # 1
        log_simulation_agent_len = len(LogSimulationAgent.objects.all())  # 1

        references[0].delete()

        """
        Is suppose when it's deleted a Competition to delete all the Rounds, GroupEnrolled,
        Simulations and SimulationsLogs. The agent is suppose to not be deleted.
        """
        self.assertEqual(len(Competition.objects.all()), competition_len - 1)
        self.assertEqual(len(Round.objects.all()), round_len - 3)
        self.assertEqual(len(Agent.objects.all()), agent_len)
        self.assertEqual(len(CompetitionAgent.objects.all()), competition_agent_len - 1)
        self.assertEqual(len(GroupEnrolled.objects.all()), group_enrolled_len - 1)
        self.assertEqual(len(Simulation.objects.all()), simulation_len - 1)
        self.assertEqual(len(LogSimulationAgent.objects.all()), log_simulation_agent_len - 1)

    def test_cascade_delete_round(self):
        references = self.cascade_setup()

        competition_len = len(Competition.objects.all())  # 2 => C1 and C2
        round_len = len(Round.objects.all())  # 4 => R1, R7, R8 e R9
        agent_len = len(Agent.objects.all())  # 1 => RQ7
        competition_agent_len = len(CompetitionAgent.objects.all())  # 1
        group_enrolled_len = len(GroupEnrolled.objects.all())  # 1
        simulation_len = len(Simulation.objects.all())  # 1
        log_simulation_agent_len = len(LogSimulationAgent.objects.all())  # 1

        references[1].delete()

        """
        Is suppose when it's deleted a Round,
        Simulations and SimulationsLogs. The agent is suppose to not be deleted.
        """
        self.assertEqual(len(Competition.objects.all()), competition_len)
        self.assertEqual(len(Round.objects.all()), round_len - 1)
        self.assertEqual(len(Agent.objects.all()), agent_len)
        self.assertEqual(len(CompetitionAgent.objects.all()), competition_agent_len - 1)
        self.assertEqual(len(GroupEnrolled.objects.all()), group_enrolled_len)
        self.assertEqual(len(Simulation.objects.all()), simulation_len - 1)
        self.assertEqual(len(LogSimulationAgent.objects.all()), log_simulation_agent_len - 1)

    def test_uploadFile(self):
        user = Account.objects.get(username="gipmon")
        client = APIClient()
        client.force_authenticate(user=user)

        url = "/api/v1/competitions/round/upload/param_list/?round=R1"
        f = open('media/tests_files/Param.xml', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Uploaded', 'message': 'The file has been uploaded and saved to R1'})

        url = "/api/v1/competitions/round/upload/grid/?round=R1"
        f = open('media/tests_files/Ciber2010_Grid.xml', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Uploaded', 'message': 'The file has been uploaded and saved to R1'})

        url = "/api/v1/competitions/round/upload/lab/?round=R1"
        f = open('media/tests_files/Ciber2010_Lab.xml', 'r')
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
        self.assertEqual(response.data, [OrderedDict([('name', u'R1'), ('parent_competition_name', u'C1')])])

        client.force_authenticate(user=None)

    def test_max_agents_colaborativa(self):
        user = Account.objects.get(username="gipmon")
        client = APIClient()
        client.force_authenticate(user=user)

        url = "/api/v1/competitions/enroll/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO3'}
        response = client.post(path=url, data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Created', 'message': 'The group has enrolled.'})

        # get my enrolled groups
        url = "/api/v1/competitions/my_enrolled_groups/gipmon/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         [OrderedDict([('competition_name', u'C1'), ('group_name', u'XPTO3'), ('valid', False)])])

        # create a agent for group
        url = "/api/v1/competitions/agent/"
        data = {'agent_name': 'KAMIKAZE1', 'group_name': 'XPTO3', 'is_virtual': False}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data,
                         OrderedDict([('agent_name', u'KAMIKAZE1'), ('is_virtual', False), ('group_name', u'XPTO3')]))

        a1 = Agent.objects.get(agent_name="KAMIKAZE1")
        a1.is_virtual = True
        a1.save()

        # create a agent for group
        url = "/api/v1/competitions/agent/"
        data = {'agent_name': 'KAMIKAZE2', 'group_name': 'XPTO3', 'is_virtual': False}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data,
                         OrderedDict([('agent_name', u'KAMIKAZE2'), ('is_virtual', False), ('group_name', u'XPTO3')]))

        a2 = Agent.objects.get(agent_name="KAMIKAZE2")
        a2.is_virtual = True
        a2.save()

        # create a agent for group
        url = "/api/v1/competitions/agent/"
        data = {'agent_name': 'KAMIKAZE3', 'group_name': 'XPTO3', 'is_virtual': False}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict(
            [('agent_name', u'KAMIKAZE3'), ('is_virtual', False), ('group_name', u'XPTO3')]))

        a3 = Agent.objects.get(agent_name="KAMIKAZE3")
        a3.is_virtual = True
        a3.save()

        # create a agent for group
        url = "/api/v1/competitions/agent/"
        data = {'agent_name': 'KAMIKAZE4', 'group_name': 'XPTO3', 'is_virtual': False}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict(
            [('agent_name', u'KAMIKAZE4'), ('is_virtual', False), ('group_name', u'XPTO3')]))

        a4 = Agent.objects.get(agent_name="KAMIKAZE4")
        a4.is_virtual = True
        a4.save()

        # create a agent for group
        url = "/api/v1/competitions/agent/"
        data = {'agent_name': 'KAMIKAZE5', 'group_name': 'XPTO3', 'is_virtual': False}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict(
            [('agent_name', u'KAMIKAZE5'), ('is_virtual', False), ('group_name', u'XPTO3')]))

        a5 = Agent.objects.get(agent_name="KAMIKAZE5")
        a5.is_virtual = True
        a5.save()

        # create a agent for group
        url = "/api/v1/competitions/agent/"
        data = {'agent_name': 'KAMIKAZE6', 'group_name': 'XPTO3', 'is_virtual': False}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict(
            [('agent_name', u'KAMIKAZE6'), ('is_virtual', False), ('group_name', u'XPTO3')]))

        a6 = Agent.objects.get(agent_name="KAMIKAZE6")
        a6.is_virtual = True
        a6.save()

        # only admin
        url = "/api/v1/competitions/toggle_group_inscription/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO3'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'status': 'Inscription toggled!', 'message': 'Inscription is now: True'})
        self.assertEqual(response.status_code, 200)

        # get competitions valid inscriptions
        url = "/api/v1/competitions/enroll/XPTO3/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         [OrderedDict([('competition_name', u'C1'), ('group_name', u'XPTO3'), ('valid', True)])])

        # associate the agent to the competition
        url = "/api/v1/competitions/associate_agent/"
        data = {'competition_name': 'C1', 'agent_name': 'KAMIKAZE1'}
        response = client.post(path=url, data=data)
        self.assertEqual(dict(response.data), {'competition_name': u'C1', 'agent_name': u'KAMIKAZE1'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(CompetitionAgent.objects.all()), 1)

        # associate the agent to the competition
        url = "/api/v1/competitions/associate_agent/"
        data = {'competition_name': 'C1', 'agent_name': 'KAMIKAZE2'}
        response = client.post(path=url, data=data)
        self.assertEqual(dict(response.data), {'competition_name': u'C1', 'agent_name': u'KAMIKAZE2'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(CompetitionAgent.objects.all()), 2)

        # associate the agent to the competition
        url = "/api/v1/competitions/associate_agent/"
        data = {'competition_name': 'C1', 'agent_name': 'KAMIKAZE3'}
        response = client.post(path=url, data=data)
        self.assertEqual(dict(response.data), {'competition_name': u'C1', 'agent_name': u'KAMIKAZE3'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(CompetitionAgent.objects.all()), 3)

        # associate the agent to the competition
        url = "/api/v1/competitions/associate_agent/"
        data = {'competition_name': 'C1', 'agent_name': 'KAMIKAZE4'}
        response = client.post(path=url, data=data)
        self.assertEqual(dict(response.data), {'competition_name': u'C1', 'agent_name': u'KAMIKAZE4'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(CompetitionAgent.objects.all()), 4)

        # associate the agent to the competition
        url = "/api/v1/competitions/associate_agent/"
        data = {'competition_name': 'C1', 'agent_name': 'KAMIKAZE5'}
        response = client.post(path=url, data=data)
        self.assertEqual(dict(response.data), {'competition_name': u'C1', 'agent_name': u'KAMIKAZE5'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(CompetitionAgent.objects.all()), 5)

        # see the agents in the competition
        url = "/api/v1/competitions/agents_by_competition_group/XPTO3/?competition_name=C1"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)

        # reach maximum agents in competition
        url = "/api/v1/competitions/associate_agent/"
        data = {'competition_name': 'C1', 'agent_name': 'KAMIKAZE6'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'status': 'Reached the limit of agents',
                                         'message': 'Reached the number of competition_agents!'})
        self.assertEqual(response.status_code, 400)

        client.force_authenticate(user=None)

    def test_max_agents_competitiva(self):
        user = Account.objects.get(username="gipmon")
        client = APIClient()
        client.force_authenticate(user=user)

        c = Competition.objects.get(name="C1")
        c.type_of_competition = settings.COMPETITIVA
        c.save()

        url = "/api/v1/competitions/enroll/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO3'}
        response = client.post(path=url, data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Created', 'message': 'The group has enrolled.'})

        # create a agent for group
        url = "/api/v1/competitions/agent/"
        data = {'agent_name': 'KAMIKAZE1', 'group_name': 'XPTO3', 'is_virtual': False}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data,
                         OrderedDict([('agent_name', u'KAMIKAZE1'), ('is_virtual', False), ('group_name', u'XPTO3')]))

        a1 = Agent.objects.get(agent_name="KAMIKAZE1")
        a1.is_virtual = True
        a1.save()

        # create a agent for group
        url = "/api/v1/competitions/agent/"
        data = {'agent_name': 'KAMIKAZE2', 'group_name': 'XPTO3', 'is_virtual': False}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data,
                         OrderedDict([('agent_name', u'KAMIKAZE2'), ('is_virtual', False), ('group_name', u'XPTO3')]))

        a2 = Agent.objects.get(agent_name="KAMIKAZE2")
        a2.is_virtual = True
        a2.save()

        # only admin
        url = "/api/v1/competitions/toggle_group_inscription/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO3'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'status': 'Inscription toggled!', 'message': 'Inscription is now: True'})
        self.assertEqual(response.status_code, 200)

        # associate the agent to the competition
        url = "/api/v1/competitions/associate_agent/"
        data = {'competition_name': 'C1', 'agent_name': 'KAMIKAZE1'}
        response = client.post(path=url, data=data)
        self.assertEqual(dict(response.data), {'competition_name': u'C1', 'agent_name': u'KAMIKAZE1'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(CompetitionAgent.objects.all()), 1)

        # reach maximum agents in competition
        url = "/api/v1/competitions/associate_agent/"
        data = {'competition_name': 'C1', 'agent_name': 'KAMIKAZE2'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'status': 'Reached the limit of agents',
                                         'message': 'Reached the number of competition_agents!'})
        self.assertEqual(response.status_code, 400)

        client.force_authenticate(user=None)

    def test_url_slug(self):
        user = Account.objects.get(username="gipmon")
        client = APIClient()
        client.force_authenticate(user=user)

        # create competition
        url = "/api/v1/competitions/crud/"
        data = {'name': 'C2.', 'type_of_competition': settings.COMPETITIVA}
        response = client.post(url, data)
        self.assertEqual(response.status_code, 400)

        # create round
        url = "/api/v1/competitions/round/"
        data = {'name': 'C2.', 'parent_competition_name': 'C1'}
        response = client.post(url, data)
        self.assertEqual(response.status_code, 400)

        client.force_authenticate(user=None)