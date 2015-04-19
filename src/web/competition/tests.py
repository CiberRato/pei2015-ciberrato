from collections import OrderedDict

from django.test import TestCase
from competition.models import *
from authentication.models import GroupMember
from rest_framework.test import APIClient


class AuthenticationTestCase(TestCase):
    def setUp(self):
        g1 = Group.objects.create(name="XPTO1", max_members=10)
        g2 = Group.objects.create(name="XPTO2", max_members=10)
        g3 = Group.objects.create(name="XPTO3", max_members=10)

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

        GroupMember.objects.create(account=a1, group=g1, is_admin=True)

        GroupMember.objects.create(account=a2, group=g2, is_admin=True)
        GroupMember.objects.create(account=a1, group=g2, is_admin=True)

        GroupMember.objects.create(account=a3, group=g3, is_admin=True)
        GroupMember.objects.create(account=a1, group=g3, is_admin=True)

    def test_enrollGroup(self):
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
        self.assertEqual(response.data, OrderedDict(
            [(u'name', u'IIA'), (u'number_teams_for_trial', 2), (u'number_agents_by_grid', 1)]))

        # list type of competition
        url = "/api/v1/competitions/type_of_competition/"
        response = client.get(url)
        self.assertEqual(response.data, OrderedDict([(u'count', 3), (u'next', None), (u'previous', None), (u'results', [
            OrderedDict([('name', u'Competitive'), ('number_teams_for_trial', 3), ('number_agents_by_grid', 1)]),
            OrderedDict([('name', u'Collaborative'), ('number_teams_for_trial', 1), ('number_agents_by_grid', 5)]),
            OrderedDict([('name', u'IIA'), ('number_teams_for_trial', 2), ('number_agents_by_grid', 1)])])]))

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
        self.assertEqual(response.data,
                         [OrderedDict([('name', u'C1'), ('type_of_competition', OrderedDict(
                             [('name', u'Collaborative'), ('number_teams_for_trial', 1),
                              ('number_agents_by_grid', 5)])), ('state_of_competition', 'Register')]), OrderedDict(
                             [('name', u'C2'), ('type_of_competition', OrderedDict(
                                 [('name', u'Competitive'), ('number_teams_for_trial', 3),
                                  ('number_agents_by_grid', 1)])), ('state_of_competition', 'Register')])])

        # get all competitions
        url = "/api/v1/competitions/get/All/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         [OrderedDict([('name', u'C1'), ('type_of_competition', OrderedDict(
                             [('name', u'Collaborative'), ('number_teams_for_trial', 1),
                              ('number_agents_by_grid', 5)])), ('state_of_competition', 'Register')]), OrderedDict(
                             [('name', u'C2'), ('type_of_competition', OrderedDict(
                                 [('name', u'Competitive'), ('number_teams_for_trial', 3),
                                  ('number_agents_by_grid', 1)])), ('state_of_competition', 'Register')])])

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
                         [OrderedDict([('competition', OrderedDict([('name', u'C1'), ('type_of_competition',
                                                                                      OrderedDict(
                                                                                          [('name', u'Collaborative'), (
                                                                                              'number_teams_for_trial',
                                                                                              1),
                                                                                           ('number_agents_by_grid',
                                                                                            5)])),
                                                                    ('state_of_competition', 'Register')])),
                                       ('group_name', u'XPTO1'), ('valid', False)])])

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
                         [OrderedDict([('competition', OrderedDict([('name', u'C1'), ('type_of_competition',
                                                                                      OrderedDict(
                                                                                          [('name', u'Collaborative'), (
                                                                                              'number_teams_for_trial',
                                                                                              1),
                                                                                           ('number_agents_by_grid',
                                                                                            5)])),
                                                                    ('state_of_competition', 'Register')])),
                                       ('group_name', u'XPTO1'), ('valid', False)]),
                          OrderedDict([('competition', OrderedDict([('name', u'C1'), ('type_of_competition',
                                                                                      OrderedDict(
                                                                                          [('name', u'Collaborative'), (
                                                                                              'number_teams_for_trial',
                                                                                              1),
                                                                                           ('number_agents_by_grid',
                                                                                            5)])),
                                                                    ('state_of_competition', 'Register')])),
                                       ('group_name', u'XPTO2'), ('valid', False)]),
                          OrderedDict([('competition', OrderedDict([('name', u'C1'), ('type_of_competition',
                                                                                      OrderedDict(
                                                                                          [('name', u'Collaborative'), (
                                                                                              'number_teams_for_trial',
                                                                                              1),
                                                                                           ('number_agents_by_grid',
                                                                                            5)])),
                                                                    ('state_of_competition', 'Register')])),
                                       ('group_name', u'XPTO3'), ('valid', False)])])

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
        url = "/api/v1/agents/agent/"
        data = {'agent_name': 'KAMIKAZE', 'group_name': 'XPTO3', 'is_local': False, 'language': 'Python'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict(
            [(u'agent_name', u'KAMIKAZE'), (u'is_local', False), (u'language', 'Python'), (u'group_name', u'XPTO3')]))

        # get agents by group
        url = "/api/v1/agents/agents_by_group/XPTO3/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = response.data[0]
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['user']['updated_at']
        del rsp['user']['created_at']

        self.assertEqual(rsp, OrderedDict(
            [('agent_name', u'KAMIKAZE'), ('is_local', False), ('rounds', []), ('language', u'Python'),
             ('competitions', []),
             ('user', OrderedDict(
                 [('email', u'rf@rf.pt'), ('username', u'gipmon'), ('teaching_institution', u'Universidade de Aveiro'),
                  ('first_name', u'Rafael'), ('last_name', u'Ferreira')])), ('group_name', u'XPTO3')]))

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
            [('agent_name', u'KAMIKAZE'), ('is_local', False), ('rounds', []), ('language', u'Python'),
             ('competitions', []),
             ('user', OrderedDict(
                 [('email', u'rf@rf.pt'), ('username', u'gipmon'), ('teaching_institution', u'Universidade de Aveiro'),
                  ('first_name', u'Rafael'), ('last_name', u'Ferreira')])), ('group_name', u'XPTO3')]))

        # get the agent information about the agent
        url = "/api/v1/agents/agent/KAMIKAZE/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)

        rsp = dict(response.data)
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['user']['updated_at']
        del rsp['user']['created_at']

        self.assertEqual(rsp,
                         {'is_local': False, 'agent_name': u'KAMIKAZE', 'language': u'Python', 'group_name': u'XPTO3',
                          'competitions': [], 'user': OrderedDict(
                             [('email', u'rf@rf.pt'), ('username', u'gipmon'),
                              ('teaching_institution', u'Universidade de Aveiro'),
                              ('first_name', u'Rafael'), ('last_name', u'Ferreira')]), 'rounds': []})

        # upload agent code
        url = "/api/v1/agents/upload/agent/?agent_name=KAMIKAZE"
        f = open('media/tests_files/myrob_do.py', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'File uploaded!', 'message': 'The agent code has been uploaded!'})

        url = "/api/v1/agents/upload/agent/?agent_name=KAMIKAZE"
        f = open('media/tests_files/main.c', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'File uploaded!', 'message': 'The agent code has been uploaded!'})

        url = "/api/v1/agents/upload/agent/?agent_name=KAMIKAZE"
        f = open('media/tests_files/main.cpp', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'File uploaded!', 'message': 'The agent code has been uploaded!'})

        url = "/api/v1/agents/upload/agent/?agent_name=KAMIKAZE"
        f = open('media/tests_files/main.java', 'r')
        response = client.post(url, {'file': f})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'File uploaded!', 'message': 'The agent code has been uploaded!'})

        url = "/api/v1/agents/agent_files/KAMIKAZE/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)

        url = "/api/v1/agents/agent_all_files/KAMIKAZE/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        url = "/api/v1/agents/file/KAMIKAZE/myrob_do.py/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        # delete uploaded file
        url = "/api/v1/agents/delete_agent_file/KAMIKAZE/?file_name=myrob_do.py"
        response = client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "Deleted", "message": "The agent file has been deleted"})

        url = "/api/v1/agents/agent/KAMIKAZE/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = dict(response.data)
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['user']['updated_at']
        del rsp['user']['created_at']

        self.assertEqual(rsp,
                         {'is_local': False, 'agent_name': u'KAMIKAZE', 'language': u'Python', 'group_name': u'XPTO3',
                          'competitions': [], 'user': OrderedDict(
                             [('email', u'rf@rf.pt'), ('username', u'gipmon'),
                              ('teaching_institution', u'Universidade de Aveiro'),
                              ('first_name', u'Rafael'), ('last_name', u'Ferreira')]), 'rounds': []})

        url = "/api/v1/agents/allowed_languages/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         [{'name': 'Python', 'value': 'Python'}, {'name': 'C', 'value': 'C'},
                          {'name': 'Java', 'value': 'Java'}, {'name': 'C++', 'value': 'cplusplus'}])

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

        url = "/api/v1/competitions/toggle_group_inscription/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO2'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'status': 'Inscription toggled!', 'message': 'Inscription is now: True'})
        self.assertEqual(response.status_code, 200)

        url = "/api/v1/competitions/toggle_group_inscription/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO1'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'status': 'Inscription toggled!', 'message': 'Inscription is now: True'})
        self.assertEqual(response.status_code, 200)

        """ grid Positions """
        # create grid position
        url = "/api/v1/competitions/grid_position/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO3'}
        response = client.post(path=url, data=data)
        identifier = response.data["identifier"]
        self.assertEqual(response.data, {'identifier': identifier, 'competition': OrderedDict([('name', u'C1'), (
            'type_of_competition',
            OrderedDict([('name', u'Collaborative'), ('number_teams_for_trial', 1), ('number_agents_by_grid', 5)])), (
                                                                                                   'state_of_competition',
                                                                                                   'Register')]),
                                         'group_name': u'XPTO3'})
        self.assertEqual(response.status_code, 201)

        # retrieve the grid position
        url = "/api/v1/competitions/grid_position/C1/?group_name=XPTO3"
        response = client.get(path=url, data=data)
        self.assertEqual(response.data, {'identifier': identifier, 'competition': OrderedDict([('name', u'C1'), (
            'type_of_competition',
            OrderedDict([('name', u'Collaborative'), ('number_teams_for_trial', 1), ('number_agents_by_grid', 5)])), (
                                                                                                   'state_of_competition',
                                                                                                   'Register')]),
                                         'group_name': u'XPTO3'})
        self.assertEqual(response.status_code, 200)

        # ADMIN retrieve the grids by competition
        url = "/api/v1/competitions/grid_positions_competition/C1/"
        response = client.get(path=url, data=data)
        self.assertEqual(response.data, [{'identifier': identifier, 'competition': OrderedDict([('name', u'C1'), (
            'type_of_competition',
            OrderedDict([('name', u'Collaborative'), ('number_teams_for_trial', 1), ('number_agents_by_grid', 5)])), (
                                                                                                    'state_of_competition',
                                                                                                    'Register')]),
                                          'group_name': u'XPTO3'}])
        self.assertEqual(response.status_code, 200)

        # list user grids
        url = "/api/v1/competitions/grid_position/"
        response = client.get(path=url)

        # associate agent to the grid
        url = "/api/v1/competitions/agent_grid/"
        data = {'grid_identifier': identifier, 'agent_name': 'KAMIKAZE', 'position': 1}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'grid_identifier': identifier, 'agent_name': 'KAMIKAZE', 'position': 1})

        # associate agent to the grid
        url = "/api/v1/competitions/agent_grid/"
        data = {'grid_identifier': identifier, 'agent_name': 'KAMIKAZE', 'position': 2}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'grid_identifier': identifier, 'agent_name': 'KAMIKAZE', 'position': 2})

        # associate agent to the grid
        url = "/api/v1/competitions/agent_grid/"
        data = {'grid_identifier': identifier, 'agent_name': 'KAMIKAZE', 'position': 3}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'grid_identifier': identifier, 'agent_name': 'KAMIKAZE', 'position': 3})

        # associate agent to the grid
        url = "/api/v1/competitions/agent_grid/"
        data = {'grid_identifier': identifier, 'agent_name': 'KAMIKAZE', 'position': 4}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'grid_identifier': identifier, 'agent_name': 'KAMIKAZE', 'position': 4})

        # agents associated to the grid
        url = "/api/v1/competitions/agent_grid/" + identifier + "/"
        response = client.get(path=url)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.status_code, 200)

        # see round files
        url = "/api/v1/competitions/round_files/R1/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'param_list': {'url': '', 'last_modification': None, 'file': '', 'size': '0B'},
                                         'grid': {'url': '', 'last_modification': None, 'file': '', 'size': '0B'},
                                         'lab': {'url': '', 'last_modification': None, 'file': '', 'size': '0B'}})

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

        # see round files
        url = "/api/v1/competitions/round_files/R1/"
        response = client.get(path=url)
        # print response.data
        # print response.status_code
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

        # see if the files were registred
        url = "/api/v1/competitions/round_admin/R1/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        # print dict(response.data) # show the round files
        self.assertEqual(len(dict(response.data)), 5)

        # create simulation (only by admin)
        url = "/api/v1/competitions/trial/"
        data = {'round_name': 'R1'}
        response = client.post(path=url, data=data)
        rsp = dict(response.data)
        del rsp['created_at']
        del rsp['updated_at']
        simulation_identifier = rsp['identifier']
        del rsp['identifier']
        self.assertEqual(rsp, {'round_name': u'R1', 'state': u'WAITING'})
        self.assertEqual(response.status_code, 201)

        # retrieve the simulation data
        url = "/api/v1/competitions/trial/" + simulation_identifier + "/"
        response = client.get(url)
        rsp = dict(response.data)
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['identifier']
        self.assertEqual(rsp, {'round_name': u'R1', 'state': u'WAITING'})
        self.assertEqual(response.status_code, 200)

        # associate GridPosition to simulation
        url = "/api/v1/competitions/simulation_grid/"
        data = {'grid_identifier': identifier, 'simulation_identifier': simulation_identifier, 'position': 1}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data,
                         {'grid_identifier': identifier, 'simulation_identifier': simulation_identifier, 'position': 1})
        self.assertEqual(response.status_code, 201)

        # get gridpositions by simulation
        url = "/api/v1/competitions/simulation_grid/" + simulation_identifier + "/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        """ END grid positions """

        # see the information about the agent
        url = "/api/v1/agents/agent/KAMIKAZE/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = dict(response.data)
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['user']['updated_at']
        del rsp['user']['created_at']

        self.assertEqual(rsp,
                         {'is_local': False, 'agent_name': u'KAMIKAZE', 'language': u'Python', 'group_name': u'XPTO3',
                          'competitions': [], 'user': OrderedDict(
                             [('email', u'rf@rf.pt'), ('username', u'gipmon'),
                              ('teaching_institution', u'Universidade de Aveiro'),
                              ('first_name', u'Rafael'), ('last_name', u'Ferreira')]), 'rounds': []})

        # start simulation
        url = "/api/v1/simulations/start/"
        data = {'trial_id': simulation_identifier}
        response = client.post(path=url, data=data)

        if response.status_code == 200:
            self.assertEqual(response.data, {'status': 'Trial started',
                                             'message': 'Please wait that the trial starts at the simulator!'})
        elif response.status_code == 400:
            self.assertEqual(response.data, {'status': 'Bad Request', 'message': 'The simulator appears to be down!'})

        # retrieve the agent list of one round
        url = "/api/v1/competitions/round_agents/R1/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = response.data
        del rsp[0]['created_at']
        del rsp[0]['updated_at']
        self.assertEqual(rsp, [OrderedDict([('round_name', u'R1'), ('agent_name', u'KAMIKAZE')])])

        # test participants for one round
        url = "/api/v1/competitions/round_participants/R1/"
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
        url = "/api/v1/competitions/round_groups/R1/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('name', u'XPTO3'), ('max_members', 10)])])

        r = Round.objects.get(name="R1")
        competition_agent = CompetitionAgent.objects.filter(round=r)
        competition_agent = competition_agent[0]
        competition_agent.eligible = False
        competition_agent.save()

        # get the simulations by agent
        url = "/api/v1/competitions/trials_by_agent/KAMIKAZE/"
        response = client.get(url)
        rsp = response.data[0]
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['identifier']
        self.assertEqual(rsp, {'round_name': u'R1', 'state': u'WAITING'})
        self.assertEqual(response.status_code, 200)

        # get the simulations by round
        url = "/api/v1/competitions/trials_by_round/R1/"
        response = client.get(url)
        rsp = response.data[0]
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['identifier']
        self.assertEqual(rsp, {'round_name': u'R1', 'state': u'WAITING'})
        self.assertEqual(response.status_code, 200)

        # get the simulations by competition
        url = "/api/v1/competitions/trials_by_competition/C1/"
        response = client.get(url)
        rsp = response.data[0]
        del rsp['created_at']
        del rsp['updated_at']
        del rsp['identifier']
        self.assertEqual(rsp, {'round_name': u'R1', 'state': u'WAITING'})
        self.assertEqual(response.status_code, 200)

        # get the simulation groups
        url = "/api/v1/competitions/trial_agents/" + simulation_identifier + "/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict(
            [('simulation_identifier', simulation_identifier), ('agent_name', u'KAMIKAZE'),
             ('round_name', u'R1'), ('pos', 1)]), OrderedDict(
            [('simulation_identifier', simulation_identifier), ('agent_name', u'KAMIKAZE'),
             ('round_name', u'R1'), ('pos', 2)]), OrderedDict(
            [('simulation_identifier', simulation_identifier), ('agent_name', u'KAMIKAZE'),
             ('round_name', u'R1'), ('pos', 3)]), OrderedDict(
            [('simulation_identifier', simulation_identifier), ('agent_name', u'KAMIKAZE'),
             ('round_name', u'R1'), ('pos', 4)])])

        # get simulation for simulate
        url = "/api/v1/simulations/get_simulation/" + simulation_identifier + "/"
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
        url = "/api/v1/simulations/simulation_log/"
        data = {'simulation_identifier': simulation_identifier, 'log_json': f}
        response = client.post(url, data)
        self.assertEqual(response.data, {'status': 'Created', 'message': 'The log has been uploaded!'})
        self.assertEqual(response.status_code, 201)
        simulation = Simulation.objects.get(identifier=simulation_identifier)
        self.assertEqual(simulation.log_json is None, False)

        # get log sent
        url = "/api/v1/competitions/get_simulation_log/" + simulation_identifier + "/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        simulation.log_json.delete()

        # create team score
        url = "/api/v1/competitions/team_score/"
        data = {'trial_id': simulation_identifier, 'team_name': 'XPTO3', 'score': 10, 'number_of_agents': 5, 'time': 10}
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
        data = {'trial_id': simulation_identifier, 'team_name': 'XPTO1', 'score': 10, 'number_of_agents': 5, 'time': 9}
        response = client.post(path=url, data=data)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.status_code, 201)

        # create team score
        url = "/api/v1/competitions/team_score/"
        data = {'trial_id': simulation_identifier, 'team_name': 'XPTO2', 'score': 10, 'number_of_agents': 3, 'time': 10}
        response = client.post(path=url, data=data)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.status_code, 201)

        # ranking by trial
        url = "/api/v1/competitions/ranking_trial/" + simulation_identifier + "/"
        response = client.get(path=url)
        rsp = response.data

        del rsp[0]['trial']["created_at"]
        del rsp[0]['trial']["updated_at"]
        del rsp[1]['trial']["created_at"]
        del rsp[1]['trial']["updated_at"]
        del rsp[2]['trial']["created_at"]
        del rsp[2]['trial']["updated_at"]

        self.assertEqual(rsp, [{"trial": {"identifier": simulation_identifier, "round_name": "R1",
                                          "state": "STARTED"},
                                "team": {"name": "XPTO1", "max_members": 10}, "score": 10, "number_of_agents": 5,
                                "time": 9}, {
                                   "trial": {"identifier": simulation_identifier, "round_name": "R1",
                                             "state": "STARTED"},
                                   "team": {"name": "XPTO3", "max_members": 10}, "score": 10, "number_of_agents": 5,
                                   "time": 10}, {
                                   "trial": {"identifier": simulation_identifier, "round_name": "R1",
                                             "state": "STARTED"},
                                   "team": {"name": "XPTO2", "max_members": 10}, "score": 10, "number_of_agents": 3,
                                   "time": 10}])

        # ranking by round
        url = "/api/v1/competitions/ranking_round/R1/"
        response = client.get(path=url)
        rsp = response.data

        del rsp[0]['trial']["created_at"]
        del rsp[0]['trial']["updated_at"]
        del rsp[1]['trial']["created_at"]
        del rsp[1]['trial']["updated_at"]
        del rsp[2]['trial']["created_at"]
        del rsp[2]['trial']["updated_at"]

        self.assertEqual(rsp, [{"trial": {"identifier": simulation_identifier, "round_name": "R1",
                                          "state": "STARTED"},
                                "team": {"name": "XPTO1", "max_members": 10}, "score": 10, "number_of_agents": 5,
                                "time": 9}, {
                                   "trial": {"identifier": simulation_identifier, "round_name": "R1",
                                             "state": "STARTED"},
                                   "team": {"name": "XPTO3", "max_members": 10}, "score": 10, "number_of_agents": 5,
                                   "time": 10}, {
                                   "trial": {"identifier": simulation_identifier, "round_name": "R1",
                                             "state": "STARTED"},
                                   "team": {"name": "XPTO2", "max_members": 10}, "score": 10, "number_of_agents": 3,
                                   "time": 10}])

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

        self.assertEqual(rsp, [{"trial": {"identifier": simulation_identifier, "round_name": "R1",
                                          "state": "STARTED"},
                                "team": {"name": "XPTO1", "max_members": 10}, "score": 10, "number_of_agents": 5,
                                "time": 9}, {
                                   "trial": {"identifier": simulation_identifier, "round_name": "R1",
                                             "state": "STARTED"},
                                   "team": {"name": "XPTO3", "max_members": 10}, "score": 10, "number_of_agents": 5,
                                   "time": 10}, {
                                   "trial": {"identifier": simulation_identifier, "round_name": "R1",
                                             "state": "STARTED"},
                                   "team": {"name": "XPTO2", "max_members": 10}, "score": 10, "number_of_agents": 3,
                                   "time": 10}])

        # delete the team score
        url = "/api/v1/competitions/team_score/" + simulation_identifier + "/?team_name=XPTO3"
        response = client.delete(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "Deleted", "message": "The team score has been deleted!"})

        # delete the team score
        url = "/api/v1/competitions/team_score/" + simulation_identifier + "/?team_name=XPTO2"
        response = client.delete(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "Deleted", "message": "The team score has been deleted!"})

        # delete the team score
        url = "/api/v1/competitions/team_score/" + simulation_identifier + "/?team_name=XPTO1"
        response = client.delete(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "Deleted", "message": "The team score has been deleted!"})

        # toggle inscription again
        url = "/api/v1/competitions/toggle_group_inscription/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO2'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'status': 'Inscription toggled!', 'message': 'Inscription is now: False'})
        self.assertEqual(response.status_code, 200)

        url = "/api/v1/competitions/toggle_group_inscription/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO1'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'status': 'Inscription toggled!', 'message': 'Inscription is now: False'})
        self.assertEqual(response.status_code, 200)

        # see my team scores
        url = "/api/v1/competitions/team_score/"
        response = client.get(path=url)
        self.assertEqual(len(response.data), 0)

        # agent code validation
        url = "/api/v1/agents/code_validation/KAMIKAZE/"
        data = {'code_valid': False, 'validation_result': 'Deu problemas com o Rafael!'}
        response = client.put(path=url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"code_valid": False, "validation_result": "Deu problemas com o Rafael!"})

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
        url = "/api/v1/competitions/agent_file/KAMIKAZE/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        for r in Round.objects.all():
            r.lab_path.delete()
            r.param_list_path.delete()
            r.grid_path.delete()


        # delete the agent associated
        url = "/api/v1/competitions/agent_grid/" + identifier + "/?position=1"
        response = client.delete(path=url)
        self.assertEqual(len(AgentGrid.objects.all()), 3)
        self.assertEqual(response.status_code, 200)

        # delete the grid position
        url = "/api/v1/competitions/simulation_grid/" + simulation_identifier + "/?position=1"
        response = client.delete(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(SimulationGrid.objects.all()), 0)

        # delete grid position
        url = "/api/v1/competitions/grid_position/C1/?group_name=XPTO3"
        response = client.delete(path=url)
        self.assertEqual(response.data, {"status": "Deleted", "message": "The grid positions has been deleted"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(GridPositions.objects.all()), 0)

        # delete the simulation data
        url = "/api/v1/competitions/trial/" + simulation_identifier + "/"
        response = client.delete(url)
        self.assertEqual(response.data, {'status': 'Deleted', 'message': 'The simulation has been deleted'})
        self.assertEqual(response.status_code, 200)

        # retrieve the simulation data
        url = "/api/v1/competitions/trial/" + simulation_identifier + "/"
        response = client.get(url)
        self.assertEqual(response.data, {u'detail': u'Not found.'})

        # destroy the agent
        url = "/api/v1/agents/agent/KAMIKAZE/"
        response = client.delete(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "Deleted", "message": "The agent has been deleted"})

        url = "/api/v1/agents/agent/KAMIKAZE/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {u'detail': u'Not found.'})

        url = "/api/v1/competitions/enroll/"
        response = client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         [OrderedDict([('competition', OrderedDict([('name', u'C1'), ('type_of_competition',
                                                                                      OrderedDict(
                                                                                          [('name', u'Collaborative'), (
                                                                                              'number_teams_for_trial',
                                                                                              1),
                                                                                           ('number_agents_by_grid',
                                                                                            5)])),
                                                                    ('state_of_competition', 'Register')])),
                                       ('group_name', u'XPTO1'), ('valid', False)]), OrderedDict([('competition',
                                                                                                   OrderedDict(
                                                                                                       [('name', u'C1'),
                                                                                                        (
                                                                                                            'type_of_competition',
                                                                                                            OrderedDict(
                                                                                                                [(
                                                                                                                     'name',
                                                                                                                     u'Collaborative'),
                                                                                                                 (
                                                                                                                     'number_teams_for_trial',
                                                                                                                     1),
                                                                                                                 (
                                                                                                                     'number_agents_by_grid',
                                                                                                                     5)])),
                                                                                                        (
                                                                                                            'state_of_competition',
                                                                                                            'Register')])),
                                                                                                  ('group_name',
                                                                                                   u'XPTO2'),
                                                                                                  ('valid', False)]),
                          OrderedDict([('competition', OrderedDict([('name', u'C1'), ('type_of_competition',
                                                                                      OrderedDict(
                                                                                          [('name', u'Collaborative'), (
                                                                                              'number_teams_for_trial',
                                                                                              1),
                                                                                           ('number_agents_by_grid',
                                                                                            5)])),
                                                                    ('state_of_competition', 'Register')])),
                                       ('group_name', u'XPTO3'), ('valid', True)])])

        # get my enrolled groups
        url = "/api/v1/competitions/my_enrolled_groups_competition/gipmon/?competition_name=C1"
        response = client.get(path=url)
        self.assertEqual([OrderedDict([('competition', OrderedDict([('name', u'C1'), ('type_of_competition',
                                                                                      OrderedDict(
                                                                                          [('name', u'Collaborative'), (
                                                                                              'number_teams_for_trial',
                                                                                              1),
                                                                                           ('number_agents_by_grid',
                                                                                            5)])),
                                                                    ('state_of_competition', 'Register')])),
                                       ('group_name', u'XPTO1'), ('valid', False)]), OrderedDict([('competition',
                                                                                                   OrderedDict(
                                                                                                       [('name', u'C1'),
                                                                                                        (
                                                                                                            'type_of_competition',
                                                                                                            OrderedDict(
                                                                                                                [(
                                                                                                                     'name',
                                                                                                                     u'Collaborative'),
                                                                                                                 (
                                                                                                                     'number_teams_for_trial',
                                                                                                                     1),
                                                                                                                 (
                                                                                                                     'number_agents_by_grid',
                                                                                                                     5)])),
                                                                                                        (
                                                                                                            'state_of_competition',
                                                                                                            'Register')])),
                                                                                                  ('group_name',
                                                                                                   u'XPTO2'),
                                                                                                  ('valid', False)]),
                          OrderedDict([('competition', OrderedDict([('name', u'C1'), ('type_of_competition',
                                                                                      OrderedDict(
                                                                                          [('name', u'Collaborative'), (
                                                                                              'number_teams_for_trial',
                                                                                              1),
                                                                                           ('number_agents_by_grid',
                                                                                            5)])),
                                                                    ('state_of_competition', 'Register')])),
                                       ('group_name', u'XPTO3'), ('valid', True)])],
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

        self.assertEqual(response.data, [OrderedDict([('name', u'C1'), ('type_of_competition', OrderedDict(
            [('name', u'Collaborative'), ('number_teams_for_trial', 1), ('number_agents_by_grid', 5)])),
                                                      ('state_of_competition', 'Register')])])
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
            [('name', u'Collaborative'), ('number_teams_for_trial', 1), ('number_agents_by_grid', 5)])),
                                                      ('state_of_competition', 'Competition')])])

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
        return
        references = []

        # competitive and colaborative methods
        colaborativa = TypeOfCompetition.objects.get(name='Collaborative')

        # create competition
        c3 = Competition.objects.create(name="C3", type_of_competition=colaborativa)
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
        return
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
        return
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
        return
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
                         [OrderedDict([('competition', OrderedDict([('name', u'C1'), ('type_of_competition',
                                                                                      OrderedDict(
                                                                                          [('name', u'Collaborative'), (
                                                                                              'number_teams_for_trial',
                                                                                              1),
                                                                                           ('number_agents_by_grid',
                                                                                            5)])),
                                                                    ('state_of_competition', 'Register')])),
                                       ('group_name', u'XPTO3'), ('valid', False)])])

        # create a agent for group
        url = "/api/v1/agents/agent/"
        data = {'agent_name': 'KAMIKAZE1', 'group_name': 'XPTO3', 'is_local': True, 'language': 'Python'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict(
            [(u'agent_name', u'KAMIKAZE1'), (u'is_local', True), (u'language', 'Python'), (u'group_name', u'XPTO3')]))
        a1 = Agent.objects.get(agent_name="KAMIKAZE1")
        self.assertEqual(a1.code_valid, True)

        # create a agent for group
        url = "/api/v1/agents/agent/"
        data = {'agent_name': 'KAMIKAZE2', 'group_name': 'XPTO3', 'is_local': True, 'language': 'Python'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict(
            [(u'agent_name', u'KAMIKAZE2'), (u'is_local', True), (u'language', 'Python'), (u'group_name', u'XPTO3')]))


        # create a agent for group
        url = "/api/v1/agents/agent/"
        data = {'agent_name': 'KAMIKAZE3', 'group_name': 'XPTO3', 'is_local': True, 'language': 'Python'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict(
            [(u'agent_name', u'KAMIKAZE3'), (u'is_local', True), (u'language', 'Python'), (u'group_name', u'XPTO3')]))

        # create a agent for group
        url = "/api/v1/agents/agent/"
        data = {'agent_name': 'KAMIKAZE4', 'group_name': 'XPTO3', 'is_local': True, 'language': 'Python'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict(
            [(u'agent_name', u'KAMIKAZE4'), (u'is_local', True), (u'language', 'Python'), (u'group_name', u'XPTO3')]))

        # create a agent for group
        url = "/api/v1/agents/agent/"
        data = {'agent_name': 'KAMIKAZE5', 'group_name': 'XPTO3', 'is_local': True, 'language': 'Python'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict(
            [(u'agent_name', u'KAMIKAZE5'), (u'is_local', True), (u'language', 'Python'), (u'group_name', u'XPTO3')]))

        # create a agent for group
        url = "/api/v1/agents/agent/"
        data = {'agent_name': 'KAMIKAZE6', 'group_name': 'XPTO3', 'is_local': True, 'language': 'Python'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict(
            [(u'agent_name', u'KAMIKAZE6'), (u'is_local', True), (u'language', 'Python'), (u'group_name', u'XPTO3')]))

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
                         [OrderedDict([('competition', OrderedDict([('name', u'C1'), ('type_of_competition',
                                                                                      OrderedDict(
                                                                                          [('name', u'Collaborative'), (
                                                                                              'number_teams_for_trial',
                                                                                              1),
                                                                                           ('number_agents_by_grid',
                                                                                            5)])),
                                                                    ('state_of_competition', 'Register')])),
                                       ('group_name', u'XPTO3'), ('valid', True)])])

        # create grid position
        url = "/api/v1/competitions/grid_position/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO3'}
        response = client.post(path=url, data=data)
        identifier = response.data["identifier"]
        self.assertEqual(response.data, {'identifier': identifier, 'competition': OrderedDict([('name', u'C1'), (
            'type_of_competition',
            OrderedDict([('name', u'Collaborative'), ('number_teams_for_trial', 1), ('number_agents_by_grid', 5)])), (
                                                                                                   'state_of_competition',
                                                                                                   'Register')]),
                                         'group_name': u'XPTO3'})
        self.assertEqual(response.status_code, 201)

        # associate agent to the grid
        for i in range(1, 6):
            url = "/api/v1/competitions/agent_grid/"
            agent = 'KAMIKAZE' + str(i), i
            data = {'grid_identifier': identifier, 'agent_name': agent[0], 'position': agent[1]}
            response = client.post(path=url, data=data)
            self.assertEqual(response.data,
                             {'grid_identifier': identifier, 'agent_name': agent[0], 'position': agent[1]})

        # clean the 4
        url = "/api/v1/competitions/agent_grid/" + identifier + "/?position=4"
        response = client.delete(path=url, data=data)

        url = "/api/v1/competitions/agent_grid/"
        agent = 'KAMIKAZE' + str(4), 4
        data = {'grid_identifier': identifier, 'agent_name': agent[0], 'position': agent[1]}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'grid_identifier': identifier, 'agent_name': agent[0], 'position': agent[1]})

        # see agents order
        url = "/api/v1/competitions/agent_grid/" + identifier + "/"
        response = client.get(path=url)
        self.assertEqual(response.data, [
            {"grid_identifier": identifier, "agent_name": "KAMIKAZE1", "position": 1},
            {"grid_identifier": identifier, "agent_name": "KAMIKAZE2", "position": 2},
            {"grid_identifier": identifier, "agent_name": "KAMIKAZE3", "position": 3},
            {"grid_identifier": identifier, "agent_name": "KAMIKAZE4", "position": 4},
            {"grid_identifier": identifier, "agent_name": "KAMIKAZE5", "position": 5}])

        url = "/api/v1/competitions/agent_grid/"
        agent = 'KAMIKAZE6', 6
        data = {'grid_identifier': identifier, 'agent_name': agent[0], 'position': agent[1]}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data,
                         {'status': 'Bad Request', 'message': 'You can not add more agents to the grid.'})

        client.force_authenticate(user=None)

    def test_max_agents_competitiva(self):
        return
        user = Account.objects.get(username="gipmon")
        client = APIClient()
        client.force_authenticate(user=user)

        # competitive and colaborative methods
        competitiva = TypeOfCompetition.objects.get(name='Competitive')

        c = Competition.objects.get(name="C1")
        c.type_of_competition = competitiva
        c.save()

        url = "/api/v1/competitions/enroll/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO3'}
        response = client.post(path=url, data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'status': 'Created', 'message': 'The group has enrolled.'})

        # create a agent for group
        url = "/api/v1/agents/agent/"
        data = {'agent_name': 'KAMIKAZE1', 'group_name': 'XPTO3', 'is_local': False, 'language': 'Python'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data,
                         OrderedDict([('agent_name', u'KAMIKAZE1'), (u'language', 'Python'),
                                      ('is_local', False), ('group_name', u'XPTO3')]))

        a1 = Agent.objects.get(agent_name="KAMIKAZE1")
        a1.is_presential = True
        a1.save()

        # create a agent for group
        url = "/api/v1/agents/agent/"
        data = {'agent_name': 'KAMIKAZE2', 'group_name': 'XPTO3', 'is_local': False, 'language': 'Python'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data,
                         OrderedDict([('agent_name', u'KAMIKAZE2'), (u'language', 'Python'),
                                      ('is_local', False), ('group_name', u'XPTO3')]))

        a2 = Agent.objects.get(agent_name="KAMIKAZE2")
        a2.is_presential = True
        a2.save()

        # only admin
        url = "/api/v1/competitions/toggle_group_inscription/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO3'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'status': 'Inscription toggled!', 'message': 'Inscription is now: True'})
        self.assertEqual(response.status_code, 200)

        # create grid position
        url = "/api/v1/competitions/grid_position/"
        data = {'competition_name': 'C1', 'group_name': 'XPTO3'}
        response = client.post(path=url, data=data)
        identifier = response.data["identifier"]
        self.assertEqual(response.data, {'identifier': identifier, 'competition': OrderedDict([('name', u'C1'), (
            'type_of_competition',
            OrderedDict([('name', u'Competitive'), ('number_teams_for_trial', 3), ('number_agents_by_grid', 1)])), (
                                                                                                   'state_of_competition',
                                                                                                   'Register')]),
                                         'group_name': u'XPTO3'})
        self.assertEqual(response.status_code, 201)

        url = "/api/v1/competitions/agent_grid/"
        agent = 'KAMIKAZE1', 1
        data = {'grid_identifier': identifier, 'agent_name': agent[0], 'position': agent[1]}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {'grid_identifier': identifier, 'agent_name': agent[0], 'position': agent[1]})

        url = "/api/v1/competitions/agent_grid/"
        agent = 'KAMIKAZE2', 2
        data = {'grid_identifier': identifier, 'agent_name': agent[0], 'position': agent[1]}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data,
                         {'status': 'Bad Request', 'message': 'You can not add more agents to the grid.'})

        client.force_authenticate(user=None)

    def test_url_slug(self):
        return
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