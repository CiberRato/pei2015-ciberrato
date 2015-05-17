from collections import OrderedDict

from django.test import TestCase
from competition.models import *
from authentication.models import TeamMember
from rest_framework.test import APIClient


class AuthenticationTestCase(TestCase):
    def setUp(self):
        g1 = Team.objects.create(name="XPTO1", max_members=10)
        g2 = Team.objects.create(name="XPTO2", max_members=10)
        g3 = Team.objects.create(name="XPTO3", max_members=10)

        TypeOfCompetition.objects.create(name='Competitive', number_teams_for_trial=3, number_agents_by_grid=1)
        colaborativa = TypeOfCompetition.objects.create(name='Collaborative', number_teams_for_trial=1,
                                                        number_agents_by_grid=5)

        c = Competition.objects.create(name="C1", type_of_competition=colaborativa)
        r = Round.objects.create(name="R1", parent_competition=c)

        a1 = Account.objects.create(email="rf@rf.pt", username="gipmon", first_name="Rafael", last_name="Ferreira",
                                    teaching_institution="Universidade de Aveiro", is_staff=True)
        a2 = Account.objects.create(email="ey@rf.pt", username="eypo", first_name="Costa", last_name="Ferreira",
                                    teaching_institution="Universidade de Aveiro")
        a3 = Account.objects.create(email="af@rf.pt", username="eypo94", first_name="Antonio", last_name="Ferreira",
                                    teaching_institution="Universidade de Aveiro")

        TeamMember.objects.create(account=a1, team=g1, is_admin=True)

        TeamMember.objects.create(account=a2, team=g2, is_admin=True)
        TeamMember.objects.create(account=a1, team=g2, is_admin=True)

        TeamMember.objects.create(account=a3, team=g3, is_admin=True)
        TeamMember.objects.create(account=a1, team=g3, is_admin=True)

    def test_enrollTeam(self):
        user = Account.objects.get(username="gipmon")
        client = APIClient()
        client.force_authenticate(user=user)

        # competitive and colaborative methods
        competitiva = TypeOfCompetition.objects.get(name='Competitive')
        colaborativa = TypeOfCompetition.objects.get(name='Collaborative')

        # create new type of competition
        url = "/api/v1/competitions/type_of_competition/"
        data = {'name': 'IIA', 'number_teams_for_trial': 2, 'number_agents_by_grid': 1}
        response = client.post(url, data)
        self.assertEqual(response.data, OrderedDict(
            [(u'name', u'IIA'), (u'number_teams_for_trial', 2), (u'number_agents_by_grid', 1)]))

        # retrieve type of competition
        url = "/api/v1/competitions/type_of_competition/IIA/"
        response = client.get(url)
        self.assertEqual(response.data, {"name": "IIA", "number_teams_for_trial": 2, "number_agents_by_grid": 1,
                                         "allow_remote_agents": False, "synchronous_simulation": False,
                                         "single_position": False, "timeout": 5})

        # list type of competition
        url = "/api/v1/competitions/type_of_competition/"
        response = client.get(url)
        self.assertEqual(response.data, OrderedDict([(u'count', 3), (u'next', None), (u'previous', None), (u'results', [
            OrderedDict([('name', u'Competitive'), ('number_teams_for_trial', 3), ('number_agents_by_grid', 1),
                         ('allow_remote_agents', False), ('synchronous_simulation', False), ('single_position', False),
                         ('timeout', 5)]), OrderedDict(
                [('name', u'Collaborative'), ('number_teams_for_trial', 1), ('number_agents_by_grid', 5),
                 ('allow_remote_agents', False), ('synchronous_simulation', False), ('single_position', False),
                 ('timeout', 5)]), OrderedDict(
                [('name', u'IIA'), ('number_teams_for_trial', 2), ('number_agents_by_grid', 1),
                 ('allow_remote_agents', False), ('synchronous_simulation', False), ('single_position', False),
                 ('timeout', 5)])])]))

        # delete type of competition
        url = "/api/v1/competitions/type_of_competition/IIA/"
        response = client.delete(url)
        self.assertEqual(response.data, {'status': 'Deleted', 'message': 'The type of competition has been deleted'})
        self.assertEqual(len(TypeOfCompetition.objects.all()), 2)

        # create competition
        url = "/api/v1/competitions/crud/"
        data = {'name': 'C2', 'type_of_competition': competitiva.name}
        response = client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict([('name', u'C2'), ('type_of_competition', competitiva.name)]))

        # get competition Register
        url = "/api/v1/competitions/get/Register/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('name', u'C1'), ('type_of_competition', OrderedDict(
            [('name', u'Collaborative'), ('number_teams_for_trial', 1), ('number_agents_by_grid', 5),
             ('allow_remote_agents', False), ('synchronous_simulation', False), ('single_position', False),
             ('timeout', 5)])), ('state_of_competition', 'Register')]), OrderedDict([('name', u'C2'), (
        'type_of_competition', OrderedDict(
            [('name', u'Competitive'), ('number_teams_for_trial', 3), ('number_agents_by_grid', 1),
             ('allow_remote_agents', False), ('synchronous_simulation', False), ('single_position', False),
             ('timeout', 5)])), ('state_of_competition', 'Register')])])
        # get all competitions
        url = "/api/v1/competitions/get/All/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('name', u'C1'), ('type_of_competition', OrderedDict(
            [('name', u'Collaborative'), ('number_teams_for_trial', 1), ('number_agents_by_grid', 5),
             ('allow_remote_agents', False), ('synchronous_simulation', False), ('single_position', False),
             ('timeout', 5)])), ('state_of_competition', 'Register')]), OrderedDict([('name', u'C2'), (
        'type_of_competition', OrderedDict(
            [('name', u'Competitive'), ('number_teams_for_trial', 3), ('number_agents_by_grid', 1),
             ('allow_remote_agents', False), ('synchronous_simulation', False), ('single_position', False),
             ('timeout', 5)])), ('state_of_competition', 'Register')])])


        # enroll one team in the competition, the team stays with the inscription valid=False
        url = "/api/v1/competitions/enroll/"
        data = {'competition_name': 'C1', 'team_name': 'XPTO1'}
        response = client.post(path=url, data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Created', 'message': 'The team has enrolled.'})

        # teams that enrolled in the competition
        url = "/api/v1/competitions/enroll/"
        response = client.get(path=url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('competition', OrderedDict([('name', u'C1'), (
        'type_of_competition', OrderedDict(
            [('name', u'Collaborative'), ('number_teams_for_trial', 1), ('number_agents_by_grid', 5),
             ('allow_remote_agents', False), ('synchronous_simulation', False), ('single_position', False),
             ('timeout', 5)])), ('state_of_competition', 'Register')])), ('team_name', u'XPTO1'), ('valid', False)])])

        # the team can't enroll twice
        url = "/api/v1/competitions/enroll/"
        data = {'competition_name': 'C1', 'team_name': 'XPTO1'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'status': 'Bad request', 'message': 'The team already enrolled.'})

        # enroll another team to the competition
        url = "/api/v1/competitions/enroll/"
        data = {'competition_name': 'C1', 'team_name': 'XPTO2'}
        response = client.post(path=url, data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Created', 'message': 'The team has enrolled.'})

        # and another one :D
        url = "/api/v1/competitions/enroll/"
        data = {'competition_name': 'C1', 'team_name': 'XPTO3'}
        response = client.post(path=url, data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Created', 'message': 'The team has enrolled.'})

        # see who are in the competition!
        url = "/api/v1/competitions/enroll/"
        response = client.get(path=url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('competition', OrderedDict([('name', u'C1'), (
        'type_of_competition', OrderedDict(
            [('name', u'Collaborative'), ('number_teams_for_trial', 1), ('number_agents_by_grid', 5),
             ('allow_remote_agents', False), ('synchronous_simulation', False), ('single_position', False),
             ('timeout', 5)])), ('state_of_competition', 'Register')])), ('team_name', u'XPTO1'), ('valid', False)]),
                                         OrderedDict([('competition', OrderedDict([('name', u'C1'), (
                                         'type_of_competition', OrderedDict(
                                             [('name', u'Collaborative'), ('number_teams_for_trial', 1),
                                              ('number_agents_by_grid', 5), ('allow_remote_agents', False),
                                              ('synchronous_simulation', False), ('single_position', False),
                                              ('timeout', 5)])), ('state_of_competition', 'Register')])),
                                                      ('team_name', u'XPTO2'), ('valid', False)]), OrderedDict([(
                                                                                                                'competition',
                                                                                                                OrderedDict(
                                                                                                                    [(
                                                                                                                     'name',
                                                                                                                     u'C1'),
                                                                                                                     (
                                                                                                                     'type_of_competition',
                                                                                                                     OrderedDict(
                                                                                                                         [
                                                                                                                             (
                                                                                                                             'name',
                                                                                                                             u'Collaborative'),
                                                                                                                             (
                                                                                                                             'number_teams_for_trial',
                                                                                                                             1),
                                                                                                                             (
                                                                                                                             'number_agents_by_grid',
                                                                                                                             5),
                                                                                                                             (
                                                                                                                             'allow_remote_agents',
                                                                                                                             False),
                                                                                                                             (
                                                                                                                             'synchronous_simulation',
                                                                                                                             False),
                                                                                                                             (
                                                                                                                             'single_position',
                                                                                                                             False),
                                                                                                                             (
                                                                                                                             'timeout',
                                                                                                                             5)])),
                                                                                                                     (
                                                                                                                     'state_of_competition',
                                                                                                                     'Register')])),
                                                                                                                (
                                                                                                                'team_name',
                                                                                                                u'XPTO3'),
                                                                                                                (
                                                                                                                'valid',
                                                                                                                False)])])

        # only admin
        url = "/api/v1/competitions/toggle_team_inscription/"
        data = {'competition_name': 'C1', 'team_name': 'XPTO3'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'status': 'Inscription toggled!', 'message': 'Inscription is now: True'})
        self.assertEqual(response.status_code, 200)

        # list of all teams enrolled and with inscriptions valid or not in one competition
        url = "/api/v1/competitions/teams/C1/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [
            OrderedDict([('team', OrderedDict([('name', u'XPTO1'), ('max_members', 10)])), ('valid', False)]),
            OrderedDict([('team', OrderedDict([('name', u'XPTO2'), ('max_members', 10)])), ('valid', False)]),
            OrderedDict([('team', OrderedDict([('name', u'XPTO3'), ('max_members', 10)])), ('valid', True)])])

        # list of all teams enrolled and with inscriptions not valid in one competition
        url = "/api/v1/competitions/teams_not_valid/C1/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('name', u'XPTO1'), ('max_members', 10)]),
                                         OrderedDict([('name', u'XPTO2'), ('max_members', 10)])])

        # only admin
        url = "/api/v1/competitions/toggle_team_inscription/"
        data = {'competition_name': 'C1', 'team_name': 'XPTO3'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'status': 'Inscription toggled!', 'message': 'Inscription is now: False'})
        self.assertEqual(response.status_code, 200)

        # list of all teams enrolled and with inscriptions not valid in one competition
        url = "/api/v1/competitions/teams_not_valid/C1/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('name', u'XPTO1'), ('max_members', 10)]),
                                         OrderedDict([('name', u'XPTO2'), ('max_members', 10)]),
                                         OrderedDict([('name', u'XPTO3'), ('max_members', 10)])])

        # list of all teams enrolled and with inscriptions valid or not in one competition
        url = "/api/v1/competitions/teams/C1/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [
            OrderedDict([('team', OrderedDict([('name', u'XPTO1'), ('max_members', 10)])), ('valid', False)]),
            OrderedDict([('team', OrderedDict([('name', u'XPTO2'), ('max_members', 10)])), ('valid', False)]),
            OrderedDict([('team', OrderedDict([('name', u'XPTO3'), ('max_members', 10)])), ('valid', False)])])

        # delete the team enroll from the competition
        url = "/api/v1/competitions/remove_enroll_team/C1/?team_name=XPTO3"
        response = client.delete(path=url)
        self.assertEqual(response.status_code, 200)

        # enroll the team again, and OK
        url = "/api/v1/competitions/enroll/"
        data = {'competition_name': 'C1', 'team_name': 'XPTO3'}
        response = client.post(path=url, data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Created', 'message': 'The team has enrolled.'})

        # create a agent for team, without code first
        url = "/api/v1/agents/agent/"
        data = {'agent_name': 'KAMIKAZE', 'team_name': 'XPTO3', 'language': 'Python'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict(
            [(u'agent_name', u'KAMIKAZE'), (u'language', 'Python'), (u'team_name', u'XPTO3')]))

        # create a agent for team, without code first
        url = "/api/v1/agents/agent/"
        data = {'agent_name': 'KAMIKAZE', 'team_name': 'XPTO1', 'language': 'Python'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict(
            [(u'agent_name', u'KAMIKAZE'), (u'language', 'Python'), (u'team_name', u'XPTO1')]))

        # get agents by team
        url = "/api/v1/agents/agents_by_team/XPTO3/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = response.data[0]
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['user']['updated_at']
        del rsp['user']['created_at']

        self.assertEqual(rsp, OrderedDict(
            [('agent_name', u'KAMIKAZE'), ('is_remote', False), ('rounds', []), ('code_valid', False),
             ('validation_result', u''), ('language', 'Python'), ('competitions', []), ('user', OrderedDict(
                [('email', u'rf@rf.pt'), ('username', u'gipmon'), ('teaching_institution', u'Universidade de Aveiro'),
                 ('first_name', u'Rafael'), ('last_name', u'Ferreira'), ('is_staff', True), ('is_superuser', False)])),
             ('team_name', u'XPTO3')]))

        # get agents by user
        url = "/api/v1/agents/agents_by_user/gipmon/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = response.data[0]
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['user']['updated_at']
        del rsp['user']['created_at']

        self.assertEqual(rsp, OrderedDict(
            [('agent_name', u'KAMIKAZE'), ('is_remote', False), ('rounds', []), ('code_valid', False),
             ('validation_result', u''), ('language', 'Python'), ('competitions', []), ('user', OrderedDict(
                [('email', u'rf@rf.pt'), ('username', u'gipmon'), ('teaching_institution', u'Universidade de Aveiro'),
                 ('first_name', u'Rafael'), ('last_name', u'Ferreira'), ('is_staff', True), ('is_superuser', False)])),
             ('team_name', u'XPTO3')]))

        # get the agent information about the agent
        url = "/api/v1/agents/agent/KAMIKAZE/?team_name=XPTO3"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)

        rsp = dict(response.data)
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['user']['updated_at']
        del rsp['user']['created_at']

        self.assertEqual(rsp,
                         {'agent_name': u'KAMIKAZE', 'language': 'Python', 'validation_result': u'', 'competitions': [],
                          'user': OrderedDict([('email', u'rf@rf.pt'), ('username', u'gipmon'),
                                               ('teaching_institution', u'Universidade de Aveiro'),
                                               ('first_name', u'Rafael'), ('last_name', u'Ferreira'),
                                               ('is_staff', True), ('is_superuser', False)]), 'is_remote': False,
                          'code_valid': False, 'rounds': [], 'team_name': u'XPTO3'})

        # upload agent code
        url = "/api/v1/agents/upload/agent/?agent_name=KAMIKAZE&team_name=XPTO3"
        f = open('media/tests_files/myrob_do.py', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'File uploaded!', 'message': 'The agent code has been uploaded!'})

        url = "/api/v1/agents/upload/agent/?agent_name=KAMIKAZE&team_name=XPTO3"
        f = open('media/tests_files/main.c', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'File uploaded!', 'message': 'The agent code has been uploaded!'})

        url = "/api/v1/agents/upload/agent/?agent_name=KAMIKAZE&team_name=XPTO3"
        f = open('media/tests_files/main.cpp', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'File uploaded!', 'message': 'The agent code has been uploaded!'})

        url = "/api/v1/agents/upload/agent/?agent_name=KAMIKAZE&team_name=XPTO3"
        f = open('media/tests_files/main.java', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'File uploaded!', 'message': 'The agent code has been uploaded!'})

        url = "/api/v1/agents/agent_files/KAMIKAZE/?team_name=XPTO3"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)

        url = "/api/v1/agents/agent_all_files/KAMIKAZE/?team_name=XPTO3"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        url = "/api/v1/agents/file/XPTO3/KAMIKAZE/myrob_do.py/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        # delete uploaded file
        url = "/api/v1/agents/delete_agent_file/KAMIKAZE/?file_name=myrob_do.py&team_name=XPTO3"
        response = client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "Deleted", "message": "The agent file has been deleted"})

        url = "/api/v1/agents/agent/KAMIKAZE/?team_name=XPTO3"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = dict(response.data)
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['user']['updated_at']
        del rsp['user']['created_at']

        self.assertEqual(rsp,
                         {'agent_name': u'KAMIKAZE', 'language': 'Python', 'validation_result': u'', 'competitions': [],
                          'user': OrderedDict([('email', u'rf@rf.pt'), ('username', u'gipmon'),
                                               ('teaching_institution', u'Universidade de Aveiro'),
                                               ('first_name', u'Rafael'), ('last_name', u'Ferreira'),
                                               ('is_staff', True), ('is_superuser', False)]), 'is_remote': False,
                          'code_valid': False, 'rounds': [], 'team_name': u'XPTO3'})

        url = "/api/v1/agents/allowed_languages/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         [{'name': 'Python', 'value': 'Python'}, {'name': 'C', 'value': 'C'},
                          {'name': 'Java', 'value': 'Java'}, {'name': 'C++', 'value': 'cplusplus'}])

        # make the code valid, this operation only can be made by the script (server validation)
        team = Team.objects.get(name="XPTO3")
        agent = Agent.objects.get(agent_name='KAMIKAZE', team=team)
        agent.code_valid = True
        agent.save()

        # only admin
        url = "/api/v1/competitions/toggle_team_inscription/"
        data = {'competition_name': 'C1', 'team_name': 'XPTO3'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'status': 'Inscription toggled!', 'message': 'Inscription is now: True'})
        self.assertEqual(response.status_code, 200)

        url = "/api/v1/competitions/toggle_team_inscription/"
        data = {'competition_name': 'C1', 'team_name': 'XPTO2'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'status': 'Inscription toggled!', 'message': 'Inscription is now: True'})
        self.assertEqual(response.status_code, 200)

        url = "/api/v1/competitions/toggle_team_inscription/"
        data = {'competition_name': 'C1', 'team_name': 'XPTO1'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'status': 'Inscription toggled!', 'message': 'Inscription is now: True'})
        self.assertEqual(response.status_code, 200)

        """ grid Positions """
        # create grid position
        url = "/api/v1/competitions/grid_position/"
        data = {'competition_name': 'C1', 'team_name': 'XPTO3'}
        response = client.post(path=url, data=data)
        identifier = response.data["identifier"]
        self.assertEqual(response.data, {'team_name': u'XPTO3', 'identifier': identifier, 'competition': OrderedDict(
            [('name', u'C1'), ('type_of_competition', OrderedDict(
                [('name', u'Collaborative'), ('number_teams_for_trial', 1), ('number_agents_by_grid', 5),
                 ('allow_remote_agents', False), ('synchronous_simulation', False), ('single_position', False),
                 ('timeout', 5)])), ('state_of_competition', 'Register')])})
        self.assertEqual(response.status_code, 201)

        # retrieve the grid position
        url = "/api/v1/competitions/grid_position/C1/?team_name=XPTO3"
        response = client.get(path=url, data=data)
        self.assertEqual(response.data, {'team_name': u'XPTO3', 'identifier': identifier, 'competition': OrderedDict(
            [('name', u'C1'), ('type_of_competition', OrderedDict(
                [('name', u'Collaborative'), ('number_teams_for_trial', 1), ('number_agents_by_grid', 5),
                 ('allow_remote_agents', False), ('synchronous_simulation', False), ('single_position', False),
                 ('timeout', 5)])), ('state_of_competition', 'Register')])})
        self.assertEqual(response.status_code, 200)

        # list user grids
        url = "/api/v1/competitions/grid_position/"
        response = client.get(path=url)

        # associate agent to the grid
        url = "/api/v1/competitions/agent_grid/"
        data = {'grid_identifier': identifier, 'agent_name': 'KAMIKAZE', 'team_name': 'XPTO3', 'position': 1}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'grid_identifier': identifier, 'agent_name': 'KAMIKAZE', 'team_name': 'XPTO3',
                                         'position': 1})


        # ADMIN retrieve the grids by competition
        url = "/api/v1/competitions/grid_positions_competition/C1/"
        response = client.get(path=url, data=data)
        self.assertEqual(response.data, [OrderedDict([('identifier', identifier), ('competition', OrderedDict(
            [('name', u'C1'), ('type_of_competition', OrderedDict(
                [('name', u'Collaborative'), ('number_teams_for_trial', 1), ('number_agents_by_grid', 5),
                 ('allow_remote_agents', False), ('synchronous_simulation', False), ('single_position', False),
                 ('timeout', 5)])), ('state_of_competition', 'Register')])), ('team_name', u'XPTO3')])])
        self.assertEqual(response.status_code, 200)

        # associate agent to the grid
        url = "/api/v1/competitions/agent_grid/"
        data = {'grid_identifier': identifier, 'agent_name': 'KAMIKAZE', 'team_name': 'XPTO3', 'position': 2}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'grid_identifier': identifier, 'agent_name': 'KAMIKAZE', 'team_name': 'XPTO3',
                                         'position': 2})

        # associate agent to the grid
        url = "/api/v1/competitions/agent_grid/"
        data = {'grid_identifier': identifier, 'agent_name': 'KAMIKAZE', 'team_name': 'XPTO3', 'position': 3}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'grid_identifier': identifier, 'agent_name': 'KAMIKAZE', 'team_name': 'XPTO3',
                                         'position': 3})

        # associate agent to the grid
        url = "/api/v1/competitions/agent_grid/"
        data = {'grid_identifier': identifier, 'agent_name': 'KAMIKAZE', 'team_name': 'XPTO3', 'position': 4}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'grid_identifier': identifier, 'agent_name': 'KAMIKAZE', 'team_name': 'XPTO3',
                                         'position': 4})

        # agents associated to the grid
        url = "/api/v1/competitions/agent_grid/" + identifier + "/"
        response = client.get(path=url)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.status_code, 200)

        # see round files
        url = "/api/v1/competitions/round_files/R1/?competition_name=C1"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'param_list': {'url': '', 'last_modification': None, 'file': '', 'size': '0B'},
                                         'grid': {'url': '', 'last_modification': None, 'file': '', 'size': '0B'},
                                         'lab': {'url': '', 'last_modification': None, 'file': '', 'size': '0B'}})

        # only  by admin
        url = "/api/v1/competitions/round/upload/param_list/?round=R1&competition_name=C1"
        f = open('media/tests_files/Param.xml', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Uploaded', 'message': 'The file has been uploaded and saved to R1'})

        # only  by admin
        url = "/api/v1/competitions/round/upload/grid/?round=R1&competition_name=C1"
        f = open('media/tests_files/Ciber2010_Grid.xml', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Uploaded', 'message': 'The file has been uploaded and saved to R1'})

        # only  by admin
        url = "/api/v1/competitions/round/upload/lab/?round=R1&competition_name=C1"
        f = open('media/tests_files/Ciber2010_Lab.xml', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Uploaded', 'message': 'The file has been uploaded and saved to R1'})

        # see round files
        url = "/api/v1/competitions/round_files/R1/?competition_name=C1"
        response = client.get(path=url)
        # print response.data
        # print response.status_code
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

        # upload resource
        url = "/api/v1/set_round_file/C1/R1/lab/"
        data = {'path': 'resources/labs/CiberRTSS2007/CiberRTSS07_FinalLab.xml'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {"status": "Uploaded", "message": "The file has been associated!"})
        self.assertEqual(response.status_code, 201)

        # see round files
        url = "/api/v1/competitions/round_files/R1/?competition_name=C1"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

        # create trial (only by admin)
        url = "/api/v1/competitions/trial/"
        data = {'round_name': 'R1', 'competition_name': 'C1'}
        response = client.post(path=url, data=data)
        rsp = dict(response.data)
        del rsp['created_at']
        del rsp['updated_at']
        trial_identifier = rsp['identifier']
        del rsp['identifier']
        self.assertEqual(rsp, {'errors': u'', 'round_name': u'R1', 'competition_name': 'C1', 'state': u'READY'})
        self.assertEqual(response.status_code, 201)

        # retrieve the trial data
        url = "/api/v1/competitions/trial/" + trial_identifier + "/"
        response = client.get(url)
        rsp = dict(response.data)
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['identifier']
        self.assertEqual(rsp, {'errors': u'', 'round_name': u'R1', 'competition_name': 'C1', 'state': u'READY'})
        self.assertEqual(response.status_code, 200)

        # associate GridPosition to trial
        url = "/api/v1/competitions/trial_grid/"
        data = {'grid_identifier': identifier, 'trial_identifier': trial_identifier, 'position': 1}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data,
                         {'grid_identifier': identifier, 'trial_identifier': trial_identifier, 'position': 1})
        self.assertEqual(response.status_code, 201)

        # get gridpositions by trial
        url = "/api/v1/competitions/trial_grid/" + trial_identifier + "/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        """ END grid positions """

        # see the information about the agent
        url = "/api/v1/agents/agent/KAMIKAZE/?team_name=XPTO3"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = dict(response.data)
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['user']['updated_at']
        del rsp['user']['created_at']

        self.assertEqual(rsp,
                         {'agent_name': u'KAMIKAZE', 'language': 'Python', 'validation_result': u'', 'competitions': [],
                          'user': OrderedDict([('email', u'rf@rf.pt'), ('username', u'gipmon'),
                                               ('teaching_institution', u'Universidade de Aveiro'),
                                               ('first_name', u'Rafael'), ('last_name', u'Ferreira'),
                                               ('is_staff', True), ('is_superuser', False)]), 'is_remote': False,
                          'code_valid': True, 'rounds': [], 'team_name': u'XPTO3'})

        # prepare trial
        url = "/api/v1/trials/prepare/"
        data = {'trial_id': trial_identifier}
        response = client.post(path=url, data=data)

        if response.status_code == 200:
            self.assertEqual(response.data,
                             {"status": "Trial started", "message": "The trial is now in \"Prepare\" state!"})
        elif response.status_code == 400:
            self.assertEqual(response.data, {'status': 'Bad Request', 'message': 'The simulator appears to be down!'})

        trial = Trial.objects.get(identifier=trial_identifier)
        trial.prepare = True
        trial.save()

        # start trial
        url = "/api/v1/trials/start/"
        data = {'trial_id': trial_identifier}
        response = client.post(path=url, data=data)

        if response.status_code == 200:
            self.assertEqual(response.data, {'status': 'Trial started',
                                             'message': 'Please wait that the trial starts at the simulator!'})
        elif response.status_code == 400:
            self.assertEqual(response.data, {'status': 'Bad Request', 'message': 'The simulator appears to be down!'})

        trial = Trial.objects.get(identifier=trial_identifier)
        trial.started = True
        trial.save()

        # test teams for one round
        url = "/api/v1/competitions/round_teams/R1/?competition_name=C1"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('name', u'XPTO3'), ('max_members', 10)])])

        r = Round.objects.get(name="R1")
        competition_agent = CompetitionAgent.objects.filter(round=r)
        competition_agent = competition_agent[0]
        competition_agent.eligible = False
        competition_agent.save()

        # get the trials by round
        url = "/api/v1/competitions/trials_by_round/R1/?competition_name=C1"
        response = client.get(url)
        rsp = response.data[0]
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['identifier']
        self.assertEqual(rsp, {'round_name': u'R1', 'competition_name': 'C1', 'state': u'STARTED', 'errors': u''})
        self.assertEqual(response.status_code, 200)

        # get the trials by competition
        url = "/api/v1/competitions/trials_by_competition/C1/?competition_name=C1"
        response = client.get(url)
        rsp = response.data[0]
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['identifier']
        self.assertEqual(rsp, {'round_name': u'R1', 'competition_name': 'C1', 'state': u'STARTED', 'errors': u''})
        self.assertEqual(response.status_code, 200)

        # get the trial teams
        url = "/api/v1/competitions/trial_agents/" + trial_identifier + "/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data, [OrderedDict(
            [('trial_identifier', trial_identifier), ('agent_name', u'KAMIKAZE'),
             ('team_name', u'XPTO3'), ('round_name', u'R1'), ('pos', 1)]), OrderedDict(
            [('trial_identifier', trial_identifier), ('agent_name', u'KAMIKAZE'),
             ('team_name', u'XPTO3'), ('round_name', u'R1'), ('pos', 2)]), OrderedDict(
            [('trial_identifier', trial_identifier), ('agent_name', u'KAMIKAZE'),
             ('team_name', u'XPTO3'), ('round_name', u'R1'), ('pos', 3)]), OrderedDict(
            [('trial_identifier', trial_identifier), ('agent_name', u'KAMIKAZE'),
             ('team_name', u'XPTO3'), ('round_name', u'R1'), ('pos', 4)])])

        # get trial for simulate
        url = "/api/v1/trials/get_trial/" + trial_identifier + "/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = response.data
        del rsp['trial_id']
        del rsp['agents']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(rsp, {'param_list': u'/api/v1/competitions/round_file/C1/R1/param_list/',
                               'lab': u'/api/v1/competitions/round_file/C1/R1/lab/',
                               'grid': u'/api/v1/competitions/round_file/C1/R1/grid/',
                               'type_of_competition': {'timeout': 5, 'name': u'Collaborative',
                                                       'allow_remote_agents': False, 'synchronous_simulation': False,
                                                       'number_teams_for_trial': 1, 'single_position': False,
                                                       'number_agents_by_grid': 5}})
        # try to send a message
        trial = Trial.objects.get(identifier=trial_identifier)
        trial.started = True
        trial.save()

        # send a message
        url = "/api/v1/trials/message/"
        data = {'trial_identifier': trial_identifier, 'message': 'Julian Calor - Another Template'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {"status": "Created", "message": "The message has been saved!"})

        # save trial logs (only server by server)
        f = open('media/tests_files/ciberOnline_log.json', 'r')
        url = "/api/v1/trials/trial_log/"
        data = {'trial_identifier': trial_identifier, 'log_json': f}
        response = client.post(url, data)
        self.assertEqual(response.data, {'status': 'Created', 'message': 'The log has been uploaded!'})
        self.assertEqual(response.status_code, 201)
        trial = Trial.objects.get(identifier=trial_identifier)
        self.assertEqual(trial.log_json is None, False)

        # get log sent
        url = "/api/v1/competitions/get_trial_log/" + trial_identifier + "/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        trial.log_json.delete()

        # save trial errors (only server by server)
        url = "/api/v1/trials/trial_error/"
        data = {'trial_identifier': trial_identifier, 'msg': "cenas"}
        response = client.post(url, data)
        self.assertEqual(response.status_code, 201)
        trial = Trial.objects.get(identifier=trial_identifier)
        self.assertEqual(trial.errors, "cenas")

        # create team score
        url = "/api/v1/competitions/team_score/"
        data = {'trial_id': trial_identifier, 'team_name': 'XPTO3', 'score': 10, 'number_of_agents': 5, 'time': 10}
        response = client.post(path=url, data=data)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.status_code, 201)

        # see my team scores
        url = "/api/v1/competitions/team_score/"
        response = client.get(path=url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data[0]), 5)
        self.assertEqual(response.status_code, 200)

        # create team score
        url = "/api/v1/competitions/team_score/"
        data = {'trial_id': trial_identifier, 'team_name': 'XPTO1', 'score': 10, 'number_of_agents': 5, 'time': 9}
        response = client.post(path=url, data=data)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.status_code, 201)

        # create team score
        url = "/api/v1/competitions/team_score/"
        data = {'trial_id': trial_identifier, 'team_name': 'XPTO2', 'score': 10, 'number_of_agents': 3, 'time': 10}
        response = client.post(path=url, data=data)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.status_code, 201)

        # ranking by trial
        url = "/api/v1/competitions/ranking_trial/" + trial_identifier + "/"
        response = client.get(path=url)
        rsp = response.data

        del rsp[0]['trial']["created_at"]
        del rsp[0]['trial']["updated_at"]
        del rsp[1]['trial']["created_at"]
        del rsp[1]['trial']["updated_at"]
        del rsp[2]['trial']["created_at"]
        del rsp[2]['trial']["updated_at"]

        self.assertEqual(rsp, [OrderedDict([('trial', OrderedDict(
            [('identifier', trial_identifier), ('round_name', u'R1'), ('competition_name', u'C1'), ('state', u'ERROR'),
             ('errors', u'cenas')])), ('team', OrderedDict([('name', u'XPTO1'), ('max_members', 10)])), ('score', 10),
                                            ('number_of_agents', 5), ('time', 9)]), OrderedDict([('trial', OrderedDict(
            [('identifier', trial_identifier), ('round_name', u'R1'), ('competition_name', u'C1'), ('state', u'ERROR'),
             ('errors', u'cenas')])), ('team', OrderedDict([('name', u'XPTO3'), ('max_members', 10)])), ('score', 10), (
                                                                                                     'number_of_agents',
                                                                                                     5),
                                                                                                 ('time', 10)]),
                               OrderedDict([('trial', OrderedDict(
                                   [('identifier', trial_identifier), ('round_name', u'R1'),
                                    ('competition_name', u'C1'), ('state', u'ERROR'), ('errors', u'cenas')])),
                                            ('team', OrderedDict([('name', u'XPTO2'), ('max_members', 10)])),
                                            ('score', 10), ('number_of_agents', 3), ('time', 10)])])

        # ranking by round
        url = "/api/v1/competitions/ranking_round/R1/?competition_name=C1"
        response = client.get(path=url)
        rsp = response.data

        del rsp[0]['trial']["created_at"]
        del rsp[0]['trial']["updated_at"]
        del rsp[1]['trial']["created_at"]
        del rsp[1]['trial']["updated_at"]
        del rsp[2]['trial']["created_at"]
        del rsp[2]['trial']["updated_at"]

        self.assertEqual(rsp, [OrderedDict([('trial', OrderedDict(
            [('identifier', trial_identifier), ('round_name', u'R1'), ('competition_name', u'C1'), ('state', u'ERROR'),
             ('errors', u'cenas')])), ('team', OrderedDict([('name', u'XPTO1'), ('max_members', 10)])), ('score', 10),
                                            ('number_of_agents', 5), ('time', 9)]), OrderedDict([('trial', OrderedDict(
            [('identifier', trial_identifier), ('round_name', u'R1'), ('competition_name', u'C1'), ('state', u'ERROR'),
             ('errors', u'cenas')])), ('team', OrderedDict([('name', u'XPTO3'), ('max_members', 10)])), ('score', 10), (
                                                                                                     'number_of_agents',
                                                                                                     5),
                                                                                                 ('time', 10)]),
                               OrderedDict([('trial', OrderedDict(
                                   [('identifier', trial_identifier), ('round_name', u'R1'),
                                    ('competition_name', u'C1'), ('state', u'ERROR'), ('errors', u'cenas')])),
                                            ('team', OrderedDict([('name', u'XPTO2'), ('max_members', 10)])),
                                            ('score', 10), ('number_of_agents', 3), ('time', 10)])])

        # ranking by competition
        url = "/api/v1/competitions/ranking_competition/C1/"
        response = client.get(path=url)
        rsp = response.data

        del rsp[0]['trial']["created_at"]
        del rsp[0]['trial']["updated_at"]
        del rsp[1]['trial']["created_at"]
        del rsp[1]['trial']["updated_at"]
        del rsp[2]['trial']["created_at"]
        del rsp[2]['trial']["updated_at"]

        self.assertEqual(rsp, [OrderedDict([('trial', OrderedDict(
            [('identifier', trial_identifier), ('round_name', u'R1'), ('competition_name', u'C1'), ('state', u'ERROR'),
             ('errors', u'cenas')])), ('team', OrderedDict([('name', u'XPTO1'), ('max_members', 10)])), ('score', 10),
                                            ('number_of_agents', 5), ('time', 9)]), OrderedDict([('trial', OrderedDict(
            [('identifier', trial_identifier), ('round_name', u'R1'), ('competition_name', u'C1'), ('state', u'ERROR'),
             ('errors', u'cenas')])), ('team', OrderedDict([('name', u'XPTO3'), ('max_members', 10)])), ('score', 10), (
                                                                                                     'number_of_agents',
                                                                                                     5),
                                                                                                 ('time', 10)]),
                               OrderedDict([('trial', OrderedDict(
                                   [('identifier', trial_identifier), ('round_name', u'R1'),
                                    ('competition_name', u'C1'), ('state', u'ERROR'), ('errors', u'cenas')])),
                                            ('team', OrderedDict([('name', u'XPTO2'), ('max_members', 10)])),
                                            ('score', 10), ('number_of_agents', 3), ('time', 10)])])


        # ranking by team in competition
        url = "/api/v1/competitions/ranking_team_competition/XPTO1/?competition_name=C1"
        response = client.get(path=url)
        self.assertEqual(len(response.data), 1)

        # update ranking
        url = "/api/v1/competitions/team_score/" + trial_identifier + "/"
        data = {'trial_id': trial_identifier, 'team_name': 'XPTO2', 'score': 14, 'number_of_agents': 3, 'time': 10}
        response = client.put(path=url, data=data)
        self.assertEqual(response.data, {'score': 14, 'number_of_agents': 3, 'time': 10})
        self.assertEqual(response.status_code, 200)

        # ranking by competition
        url = "/api/v1/competitions/ranking_competition/C1/"
        response = client.get(path=url)
        rsp = response.data

        del rsp[0]['trial']["created_at"]
        del rsp[0]['trial']["updated_at"]
        del rsp[1]['trial']["created_at"]
        del rsp[1]['trial']["updated_at"]
        del rsp[2]['trial']["created_at"]
        del rsp[2]['trial']["updated_at"]

        self.assertEqual(rsp, [OrderedDict([('trial', OrderedDict(
            [('identifier', trial_identifier), ('round_name', u'R1'), ('competition_name', u'C1'), ('state', u'ERROR'),
             ('errors', u'cenas')])), ('team', OrderedDict([('name', u'XPTO1'), ('max_members', 10)])), ('score', 10),
                                            ('number_of_agents', 5), ('time', 9)]), OrderedDict([('trial', OrderedDict(
            [('identifier', trial_identifier), ('round_name', u'R1'), ('competition_name', u'C1'), ('state', u'ERROR'),
             ('errors', u'cenas')])), ('team', OrderedDict([('name', u'XPTO3'), ('max_members', 10)])), ('score', 10), (
                                                                                                     'number_of_agents',
                                                                                                     5),
                                                                                                 ('time', 10)]),
                               OrderedDict([('trial', OrderedDict(
                                   [('identifier', trial_identifier), ('round_name', u'R1'),
                                    ('competition_name', u'C1'), ('state', u'ERROR'), ('errors', u'cenas')])),
                                            ('team', OrderedDict([('name', u'XPTO2'), ('max_members', 10)])),
                                            ('score', 14), ('number_of_agents', 3), ('time', 10)])])

        # delete the team score
        url = "/api/v1/competitions/team_score/" + trial_identifier + "/?team_name=XPTO3"
        response = client.delete(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "Deleted", "message": "The team score has been deleted!"})

        # delete the team score
        url = "/api/v1/competitions/team_score/" + trial_identifier + "/?team_name=XPTO2"
        response = client.delete(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "Deleted", "message": "The team score has been deleted!"})

        # delete the team score
        url = "/api/v1/competitions/team_score/" + trial_identifier + "/?team_name=XPTO1"
        response = client.delete(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "Deleted", "message": "The team score has been deleted!"})

        # create automatic team score
        url = "/api/v1/competitions/automatic_score/"
        data = {'trial_id': trial_identifier, 'score': 10, 'number_of_agents': 5, 'time': 10}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {"detail":"This is not a Hall of fame competition"})

        # toggle inscription again
        url = "/api/v1/competitions/toggle_team_inscription/"
        data = {'competition_name': 'C1', 'team_name': 'XPTO2'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'status': 'Inscription toggled!', 'message': 'Inscription is now: False'})
        self.assertEqual(response.status_code, 200)

        url = "/api/v1/competitions/toggle_team_inscription/"
        data = {'competition_name': 'C1', 'team_name': 'XPTO1'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'status': 'Inscription toggled!', 'message': 'Inscription is now: False'})
        self.assertEqual(response.status_code, 200)

        # see my team scores
        url = "/api/v1/competitions/team_score/"
        response = client.get(path=url)
        self.assertEqual(len(response.data), 0)

        # agent code validation
        url = "/api/v1/agents/code_validation/KAMIKAZE/"
        data = {'team_name': 'XPTO3', 'code_valid': False, 'validation_result': 'Deu problemas com o Rafael!'}
        response = client.put(path=url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'team_name': 'XPTO3', "code_valid": False,
                                         "validation_result": "Deu problemas com o Rafael!"})

        # get round file: param_list
        url = "/api/v1/competitions/round_file/C1/R1/param_list/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        # get round file: grid
        url = "/api/v1/competitions/round_file/C1/R1/grid/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        # get round file: lab
        url = "/api/v1/competitions/round_file/C1/R1/lab/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        # get the agent files
        url = "/api/v1/agents/agent_file/XPTO3/KAMIKAZE/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        for r in Round.objects.all():
            if r.lab_can_delete:
                r.lab_path.delete()
            if r.param_list_can_delete:
                r.param_list_path.delete()
            if r.grid_can_delete:
                r.grid_path.delete()

        # delete the agent associated
        url = "/api/v1/competitions/agent_grid/" + identifier + "/?position=1"
        response = client.delete(path=url)
        self.assertEqual(len(AgentGrid.objects.all()), 3)
        self.assertEqual(response.status_code, 200)

        # delete the grid position
        url = "/api/v1/competitions/trial_grid/" + trial_identifier + "/?position=1"
        response = client.delete(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(TrialGrid.objects.all()), 0)

        # delete grid position
        url = "/api/v1/competitions/grid_position/C1/?team_name=XPTO3"
        response = client.delete(path=url)
        self.assertEqual(response.data, {"status": "Deleted", "message": "The grid positions has been deleted"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(GridPositions.objects.all()), 0)

        # set

        # delete the trial data
        url = "/api/v1/competitions/trial/" + trial_identifier + "/"
        response = client.delete(url)
        self.assertEqual(response.data, {'status': 'Deleted', 'message': 'The trial has been deleted'})
        self.assertEqual(response.status_code, 200)

        # retrieve the trial data
        url = "/api/v1/competitions/trial/" + trial_identifier + "/"
        response = client.get(url)
        self.assertEqual(response.data, {u'detail': u'Not found.'})

        # destroy the agent
        url = "/api/v1/agents/agent/KAMIKAZE/?team_name=XPTO3"
        response = client.delete(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "Deleted", "message": "The agent has been deleted"})

        url = "/api/v1/agents/agent/KAMIKAZE/?team_name=XPTO3"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {u'detail': u'Not found.'})

        url = "/api/v1/competitions/enroll/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('competition', OrderedDict([('name', u'C1'), (
        'type_of_competition', OrderedDict(
            [('name', u'Collaborative'), ('number_teams_for_trial', 1), ('number_agents_by_grid', 5),
             ('allow_remote_agents', False), ('synchronous_simulation', False), ('single_position', False),
             ('timeout', 5)])), ('state_of_competition', 'Register')])), ('team_name', u'XPTO1'), ('valid', False)]),
                                         OrderedDict([('competition', OrderedDict([('name', u'C1'), (
                                         'type_of_competition', OrderedDict(
                                             [('name', u'Collaborative'), ('number_teams_for_trial', 1),
                                              ('number_agents_by_grid', 5), ('allow_remote_agents', False),
                                              ('synchronous_simulation', False), ('single_position', False),
                                              ('timeout', 5)])), ('state_of_competition', 'Register')])),
                                                      ('team_name', u'XPTO2'), ('valid', False)]), OrderedDict([(
                                                                                                                'competition',
                                                                                                                OrderedDict(
                                                                                                                    [(
                                                                                                                     'name',
                                                                                                                     u'C1'),
                                                                                                                     (
                                                                                                                     'type_of_competition',
                                                                                                                     OrderedDict(
                                                                                                                         [
                                                                                                                             (
                                                                                                                             'name',
                                                                                                                             u'Collaborative'),
                                                                                                                             (
                                                                                                                             'number_teams_for_trial',
                                                                                                                             1),
                                                                                                                             (
                                                                                                                             'number_agents_by_grid',
                                                                                                                             5),
                                                                                                                             (
                                                                                                                             'allow_remote_agents',
                                                                                                                             False),
                                                                                                                             (
                                                                                                                             'synchronous_simulation',
                                                                                                                             False),
                                                                                                                             (
                                                                                                                             'single_position',
                                                                                                                             False),
                                                                                                                             (
                                                                                                                             'timeout',
                                                                                                                             5)])),
                                                                                                                     (
                                                                                                                     'state_of_competition',
                                                                                                                     'Register')])),
                                                                                                                (
                                                                                                                'team_name',
                                                                                                                u'XPTO3'),
                                                                                                                (
                                                                                                                'valid',
                                                                                                                True)])])

        # get my enrolled teams
        url = "/api/v1/competitions/my_enrolled_teams_competition/gipmon/?competition_name=C1"
        response = client.get(path=url)
        self.assertEqual([OrderedDict([('competition', OrderedDict([('name', u'C1'), ('type_of_competition',
                                                                                      OrderedDict(
                                                                                          [('name', u'Collaborative'), (
                                                                                          'number_teams_for_trial', 1),
                                                                                           ('number_agents_by_grid', 5),
                                                                                           ('allow_remote_agents',
                                                                                            False), (
                                                                                           'synchronous_simulation',
                                                                                           False),
                                                                                           ('single_position', False),
                                                                                           ('timeout', 5)])),
                                                                    ('state_of_competition', 'Register')])),
                                       ('team_name', u'XPTO1'), ('valid', False)]), OrderedDict([('competition',
                                                                                                  OrderedDict(
                                                                                                      [('name', u'C1'),
                                                                                                       (
                                                                                                       'type_of_competition',
                                                                                                       OrderedDict([(
                                                                                                                    'name',
                                                                                                                    u'Collaborative'),
                                                                                                                    (
                                                                                                                    'number_teams_for_trial',
                                                                                                                    1),
                                                                                                                    (
                                                                                                                    'number_agents_by_grid',
                                                                                                                    5),
                                                                                                                    (
                                                                                                                    'allow_remote_agents',
                                                                                                                    False),
                                                                                                                    (
                                                                                                                    'synchronous_simulation',
                                                                                                                    False),
                                                                                                                    (
                                                                                                                    'single_position',
                                                                                                                    False),
                                                                                                                    (
                                                                                                                    'timeout',
                                                                                                                    5)])),
                                                                                                       (
                                                                                                       'state_of_competition',
                                                                                                       'Register')])), (
                                                                                                 'team_name', u'XPTO2'),
                                                                                                 ('valid', False)]),
                          OrderedDict([('competition', OrderedDict([('name', u'C1'), ('type_of_competition',
                                                                                      OrderedDict(
                                                                                          [('name', u'Collaborative'), (
                                                                                          'number_teams_for_trial', 1),
                                                                                           ('number_agents_by_grid', 5),
                                                                                           ('allow_remote_agents',
                                                                                            False), (
                                                                                           'synchronous_simulation',
                                                                                           False),
                                                                                           ('single_position', False),
                                                                                           ('timeout', 5)])),
                                                                    ('state_of_competition', 'Register')])),
                                       ('team_name', u'XPTO3'), ('valid', True)])], response.data)
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

        # get team enrolled competitions
        url = "/api/v1/competitions/team_enrolled_competitions/XPTO3/"
        response = client.get(url)

        self.assertEqual(response.data, [OrderedDict([('name', u'C1'), ('type_of_competition', OrderedDict(
            [('name', u'Collaborative'), ('number_teams_for_trial', 1), ('number_agents_by_grid', 5),
             ('allow_remote_agents', False), ('synchronous_simulation', False), ('single_position', False),
             ('timeout', 5)])), ('state_of_competition', 'Register')])])
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
        self.assertEqual(response.data, [OrderedDict([('name', u'C1'), ('type_of_competition', OrderedDict(
            [('name', u'Collaborative'), ('number_teams_for_trial', 1), ('number_agents_by_grid', 5),
             ('allow_remote_agents', False), ('synchronous_simulation', False), ('single_position', False),
             ('timeout', 5)])), ('state_of_competition', 'Competition')])])

        r3 = Round.objects.get(name="R3")
        r3.delete()

        r2 = Round.objects.get(name="R2")
        r2.delete()

        url = "/api/v1/competitions/round/R1/?competition_name=C1"
        response = client.delete(url)
        self.assertEqual(response.status_code, 200)

        client.force_authenticate(user=None)

    def test_uploadFile(self):
        user = Account.objects.get(username="gipmon")
        client = APIClient()
        client.force_authenticate(user=user)

        url = "/api/v1/competitions/round/upload/param_list/?round=R1&competition_name=C1"
        f = open('media/tests_files/Param.xml', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Uploaded', 'message': 'The file has been uploaded and saved to R1'})

        url = "/api/v1/competitions/round/upload/grid/?round=R1&competition_name=C1"
        f = open('media/tests_files/Ciber2010_Grid.xml', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Uploaded', 'message': 'The file has been uploaded and saved to R1'})

        url = "/api/v1/competitions/round/upload/lab/?round=R1&competition_name=C1"
        f = open('media/tests_files/Ciber2010_Lab.xml', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Uploaded', 'message': 'The file has been uploaded and saved to R1'})

        url = "/api/v1/competitions/round/R1/?competition_name=C1"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        for r in Round.objects.all():
            r.lab_path.delete()
            r.param_list_path.delete()
            r.grid_path.delete()

        client.force_authenticate(user=None)

    def test_private_competitions(self):
        user = Account.objects.get(username="gipmon")
        client = APIClient()
        client.force_authenticate(user=user)

        # lets start to create another team for the current logged user
        url = "/api/v1/teams/crud/"
        data = {'name': 'TestTeam', 'max_members': 10}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict([('name', u'TestTeam'), ('max_members', 10)]))

        # now it should have for this logged user at least one private competition
        url = "/api/v1/competitions/private/list/"
        response = client.get(path=url)
        rsp = response.data
        competition_name = rsp[0]['competition']['name']
        del rsp[0]['competition']['name']
        self.assertEqual(rsp, [{'number_of_trials': 0, 'number_of_rounds': 0, 'competition': {'state_of_competition': 'Competition', 'type_of_competition': OrderedDict([('name', u'Private Competition'), ('number_teams_for_trial', 1), ('number_agents_by_grid', 50), ('allow_remote_agents', False), ('synchronous_simulation', True), ('single_position', False), ('timeout', 1)])}, 'team': u'TestTeam'}])

        # this round must have no rounds
        url = "/api/v1/competitions/private/rounds/" + competition_name + "/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

        # now let's create one round for this competition based on the files
        url = "/api/v1/competitions/private/round/"
        data = {'competition_name': competition_name,
                'grid': 'resources/grids/CiberRato2005/Ciber2005_FinalGrid.xml',
                'param_list': 'resources/param_lists/param.xml',
                'lab': 'resources/labs/CiberRato2006/Ciber2006_FinalLab.xml'}
        response = client.post(path=url, data=data)
        rsp = response.data
        round_name = rsp['name']
        del rsp['name']
        del rsp['created_at']
        del rsp['updated_at']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(rsp, {'param_list': u'param.xml', 'lab': u'Ciber2006_FinalLab.xml',
                               'grid': u'Ciber2005_FinalGrid.xml'})

        # an error round
        url = "/api/v1/competitions/private/round/"
        data = {'competition_name': competition_name,
                'grid': 'resources/grids/CiberRato2005/Ciber2005_FinalGridx.xml',
                'param_list': 'resources/grids/CiberRato2005/Ciber2005_FinalxGrid.xml',
                'lab': 'resources/grids/CiberRato2005/Ciber2005_FinalGrid.xmxl'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"status": "Bad request", "message": "The file doesn't exists!"})

        # this round must have one round
        url = "/api/v1/competitions/private/rounds/" + competition_name + "/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        rsp = response.data
        del rsp[0]['name']
        del rsp[0]['created_at']
        del rsp[0]['updated_at']
        self.assertEqual(rsp, [
            {'param_list': u'param.xml', 'lab': u'Ciber2006_FinalLab.xml', 'grid': u'Ciber2005_FinalGrid.xml'}])

        # now let's get the files name for this round and the trials list
        url = "/api/v1/competitions/private/round/" + str(round_name) + "/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        rsp = response.data
        del rsp['round']['name']
        del rsp['round']['created_at']
        del rsp['round']['updated_at']
        self.assertEqual(rsp, {'trials': [], 'round': {'param_list': u'param.xml', 'lab': u'Ciber2006_FinalLab.xml',
                                                       'grid': u'Ciber2005_FinalGrid.xml'}})

        # now let's launch one trial for that round
        url = "/api/v1/competitions/private/launch_trial/"
        data = {'round_name': round_name}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"status": "Bad request", "message": "Your Grid must have at least one agent!"})

        # create one agent
        team = Team.objects.get(name="TestTeam")
        Agent.objects.create(user=user, team=team, agent_name="KAMIKAZE", code_valid=True)

        grid_identifier = GridPositions.objects.first()
        grid_identifier = grid_identifier.identifier

        # associate to the grid position
        url = "/api/v1/competitions/agent_grid/"
        data = {'grid_identifier': grid_identifier, 'agent_name': 'KAMIKAZE', 'team_name': 'TestTeam', 'position': 1}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'grid_identifier': grid_identifier, 'agent_name': 'KAMIKAZE',
                                         'team_name': 'TestTeam', 'position': 1})
        rsp = response.data
        del rsp['grid_identifier']
        self.assertEqual(rsp,
                         OrderedDict([(u'agent_name', u'KAMIKAZE'), (u'team_name', u'TestTeam'), (u'position', 1)]))

        # now let's launch one trial for that round
        url = "/api/v1/competitions/private/launch_trial/"
        data = {'round_name': round_name}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"status": "Bad Request", "message": "The simulator appears to be down!"})

        # let see the stats
        url = "/api/v1/competitions/private/list/"
        response = client.get(path=url)
        rsp = response.data
        del rsp[0]['competition']['name']
        self.assertEqual(rsp, [{'number_of_trials': 1, 'number_of_rounds': 1, 'competition': {'state_of_competition': 'Competition', 'type_of_competition': OrderedDict([('name', u'Private Competition'), ('number_teams_for_trial', 1), ('number_agents_by_grid', 50), ('allow_remote_agents', False), ('synchronous_simulation', True), ('single_position', False), ('timeout', 1)])}, 'team': u'TestTeam'}])

        trial = Trial.objects.all()
        trial_identifier = trial[0].identifier

        # delete the trial
        url = "/api/v1/competitions/private/trial/" + trial_identifier + "/"
        response = client.delete(path=url)
        self.assertEqual(response.data, {'status': 'Deleted', 'message': 'The solo trial has been deleted!'})
        self.assertEqual(Trial.objects.all().count(), 0)

        # delete the round
        url = "/api/v1/competitions/private/round/" + str(round_name) + "/"
        response = client.delete(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "Deleted", "message": "The solo trials had been deleted!"})
        self.assertEqual(Round.objects.all().count(), 1)

        # see round resource file
        url = "/api/v1/resources_file/"
        data = {'path': 'resources/grids/CiberRato2010/Ciber2010_Grid.xml'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 200)

        client.force_authenticate(user=None)

    def test_url_slug(self):
        user = Account.objects.get(username="gipmon")
        client = APIClient()
        client.force_authenticate(user=user)

        # competitive and colaborative methods
        competitiva = TypeOfCompetition.objects.get(name='Competitive')
        colaborativa = TypeOfCompetition.objects.get(name='Collaborative')

        # create competition
        url = "/api/v1/competitions/crud/"
        data = {'name': 'C2.', 'type_of_competition': competitiva.name}
        response = client.post(url, data)
        self.assertEqual(response.status_code, 400)

        # create round
        url = "/api/v1/competitions/round/"
        data = {'name': 'C2.', 'parent_competition_name': 'C1'}
        response = client.post(url, data)
        self.assertEqual(response.status_code, 400)

        client.force_authenticate(user=None)