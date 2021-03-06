from collections import OrderedDict

from django.test import TestCase
from authentication.models import Team, TeamMember, Account
from rest_framework.test import APIClient


class TeamsModelsTestCase(TestCase):
    def setUp(self):
        g = Team.objects.create(name="XPTO", max_members=10)
        a1 = Account.objects.create(email="rf@rf.pt", username="gipmon", first_name="Rafael", last_name="Ferreira",
                                    teaching_institution="Universidade de Aveiro")
        a2 = Account.objects.create(email="ey@rf.pt", username="eypo", first_name="Costa", last_name="Ferreira",
                                    teaching_institution="Universidade de Aveiro")
        Account.objects.create(email="af@rf.pt", username="eypo94", first_name="Antonio", last_name="Ferreira",
                               teaching_institution="Universidade de Aveiro")
        TeamMember.objects.create(account=a1, team=g)
        TeamMember.objects.create(account=a2, team=g)

    def test_account_details(self):
        a1 = Account.objects.get(username="gipmon")
        a2 = Account.objects.get(username="eypo")

        self.assertEqual(a1.email, "rf@rf.pt")
        self.assertEqual(a1.username, "gipmon")
        self.assertEqual(a1.first_name, "Rafael")
        self.assertEqual(a1.last_name, "Ferreira")
        self.assertEqual(a1.teaching_institution, "Universidade de Aveiro")

        self.assertEqual(a2.email, "ey@rf.pt")
        self.assertEqual(a2.username, "eypo")
        self.assertEqual(a2.first_name, "Costa")
        self.assertEqual(a2.last_name, "Ferreira")
        self.assertEqual(a2.teaching_institution, "Universidade de Aveiro")

    def test_team_details(self):
        team = Team.objects.get(name="XPTO")
        self.assertEqual(team.name, "XPTO")
        self.assertEqual(team.max_members, 10)

    def test_team_members(self):
        a1 = Account.objects.get(username="gipmon")
        a2 = Account.objects.get(username="eypo")

        gm1 = TeamMember.objects.get(account=a1)
        gm2 = TeamMember.objects.get(account=a2)

        self.equal = self.assertEqual(str(gm1), str(a1) + " is in team XPTO (as False)")
        self.assertEqual(str(gm2), str(a2) + " is in team XPTO (as False)")

    def test_teams(self):
        user = Account.objects.get(username="gipmon")
        client = APIClient()
        client.force_authenticate(user=user)

        url = "/api/v1/teams/crud/"

        # only one team is stored
        response = client.get(url)
        self.assertEqual(response.data, OrderedDict([(u'count', 1), (u'next', None), (u'previous', None), (
            u'results', [OrderedDict([('name', u'XPTO'), ('max_members', 10)])])]))

        # create a team
        data = {'name': 'TestTeam', 'max_members': 10}
        response = client.post(path=url, data=data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict([('name', u'TestTeam'), ('max_members', 10)]))

        # only two teams must be stored
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, OrderedDict([(u'count', 2), (u'next', None), (u'previous', None), (u'results', [
            OrderedDict([('name', u'XPTO'), ('max_members', 10)]),
            OrderedDict([('name', u'TestTeam'), ('max_members', 10)])])]))

        # only two teams must be admin
        url = "/api/v1/teams/user_admin/gipmon/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('name', u'TestTeam'), ('max_members', 10)])])

        # the user must be administrator of the team
        url = "/api/v1/teams/member/TestTeam/?username=gipmon"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = dict(response.data)
        del rsp['account']['updated_at']
        del rsp['account']['created_at']
        self.assertEqual(rsp, {'account': OrderedDict(
            [('email', u'rf@rf.pt'), ('username', u'gipmon'), ('teaching_institution', u'Universidade de Aveiro'),
             ('first_name', u'Rafael'), ('last_name', u'Ferreira'), ('is_staff', False), ('is_superuser', False)]),
                               'is_admin': True, 'team': OrderedDict([('name', u'TestTeam'), ('max_members', 10)])})

        # only one member in the team
        url = "/api/v1/teams/members/TestTeam/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        # add one member to the team
        url = "/api/v1/teams/member/"
        data = {'team_name': 'TestTeam', 'user_name': 'eypo'}
        response = client.post(path=url, data=data, format='json')

        self.assertEqual(response.status_code, 201)
        rsp = dict(response.data)
        del rsp['account']['updated_at']
        del rsp['account']['created_at']
        self.assertEqual(rsp, {'account': OrderedDict(
            [('email', u'ey@rf.pt'), ('username', u'eypo'), ('teaching_institution', u'Universidade de Aveiro'),
             ('first_name', u'Costa'), ('last_name', u'Ferreira'), ('is_staff', False), ('is_superuser', False)]),
                               'is_admin': False, 'team': OrderedDict([('name', u'TestTeam'), ('max_members', 10)])})

        # verify if the user is in the team and is not an admin
        url = "/api/v1/teams/member/TestTeam/?username=eypo"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = dict(response.data)
        del rsp['account']['updated_at']
        del rsp['account']['created_at']

        self.assertEqual(rsp, {'account': OrderedDict(
            [('email', u'ey@rf.pt'), ('username', u'eypo'), ('teaching_institution', u'Universidade de Aveiro'),
             ('first_name', u'Costa'), ('last_name', u'Ferreira'), ('is_staff', False), ('is_superuser', False)]),
                               'is_admin': False, 'team': OrderedDict([('name', u'TestTeam'), ('max_members', 10)])})

        # only two members in the team
        url = "/api/v1/teams/members/TestTeam/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        # make the user a team admin
        url = "/api/v1/teams/admin/TestTeam/?username=eypo"
        response = client.put(url)
        self.assertEqual(response.status_code, 200)
        rsp = dict(response.data)
        del rsp['account']['updated_at']
        del rsp['account']['created_at']

        self.assertEqual(rsp, {'account': OrderedDict(
            [('email', u'ey@rf.pt'), ('username', u'eypo'), ('teaching_institution', u'Universidade de Aveiro'),
             ('first_name', u'Costa'), ('last_name', u'Ferreira'), ('is_staff', False), ('is_superuser', False)]),
                               'is_admin': True, 'team': OrderedDict([('name', u'TestTeam'), ('max_members', 10)])})

        # delete the user from the admins list
        url = "/api/v1/teams/admin/TestTeam/?username=eypo"
        response = client.put(url)
        self.assertEqual(response.status_code, 200)
        rsp = dict(response.data)
        del rsp['account']['updated_at']
        del rsp['account']['created_at']

        self.assertEqual(rsp, {'account': OrderedDict(
            [('email', u'ey@rf.pt'), ('username', u'eypo'), ('teaching_institution', u'Universidade de Aveiro'),
             ('first_name', u'Costa'), ('last_name', u'Ferreira'), ('is_staff', False), ('is_superuser', False)]),
                               'is_admin': False, 'team': OrderedDict([('name', u'TestTeam'), ('max_members', 10)])})

        # delete the user from the grou
        url = "/api/v1/teams/member/TestTeam/?username=eypo"
        response = client.delete(url)
        self.assertEqual(response.status_code, 200)

        # only one member in the team
        url = "/api/v1/teams/members/TestTeam/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        # add the user again
        url = "/api/v1/teams/member/"
        data = {'team_name': 'TestTeam', 'user_name': 'eypo'}
        response = client.post(path=url, data=data, format='json')

        self.assertEqual(response.status_code, 201)
        rsp = dict(response.data)
        del rsp['account']['updated_at']
        del rsp['account']['created_at']

        self.assertEqual(rsp, {'account': OrderedDict(
            [('email', u'ey@rf.pt'), ('username', u'eypo'), ('teaching_institution', u'Universidade de Aveiro'),
             ('first_name', u'Costa'), ('last_name', u'Ferreira'), ('is_staff', False), ('is_superuser', False)]),
                               'is_admin': False, 'team': OrderedDict([('name', u'TestTeam'), ('max_members', 10)])})

        # update the team
        url = "/api/v1/teams/crud/TestTeam/"
        data = {'name': "XPTO2", 'max_members': 10}
        response = client.put(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'status': 'Updated', 'message': 'The team has been updated.'})

        # test update with wrong params
        url = "/api/v1/teams/crud/XPTO2/"
        data = {'name': '', 'max_members': -1}
        response = client.put(path=url, data=data, format='json')
        self.assertEqual(response.data, {'status': 'Bad request', 'message': {
            'max_members': [u'Ensure this value is greater than or equal to 1.'],
            'name': [u'This field may not be blank.']}})
        self.assertEqual(response.status_code, 400)

        # see if has been updated
        url = "/api/v1/teams/crud/XPTO2/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'max_members': 10, 'name': u'XPTO2'})

        # delete the team
        url = "/api/v1/teams/crud/XPTO2/"
        response = client.delete(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         {'status': 'Deleted', 'message': 'The team has been deleted and the team members too.'})

        # the team not found
        url = "/api/v1/teams/members/XPTO2/"
        response = client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {u'detail': u'Not found.'})

        # no TeamMembers instances
        # two from the SetUp
        self.assertEqual(len(TeamMember.objects.all()), 2)

        client.force_authenticate(user=None)

    def test_teams_unauthenticated(self):
        client = APIClient()

        # create a team
        url = "/api/v1/teams/crud/"
        data = {'name': 'TestTeam', 'max_members': 10}
        response = client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {u'detail': u'Authentication credentials were not provided.'})

        # get team details
        url = "/api/v1/teams/crud/XPTO/"
        response = client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {u'detail': u'Authentication credentials were not provided.'})

        # destroy team
        url = "/api/v1/teams/crud/XPTO/"
        response = client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {u'detail': u'Authentication credentials were not provided.'})

        # user teams
        url = "/api/v1/teams/user/gipmon/"
        response = client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {u'detail': u'Authentication credentials were not provided.'})

        # user teams
        url = "/api/v1/teams/members/gipmon/"
        response = client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {u'detail': u'Authentication credentials were not provided.'})

        # Add user to a team
        url = "/api/v1/teams/member/"
        response = client.post(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {u'detail': u'Authentication credentials were not provided.'})

        # Delete an user from a team
        url = "/api/v1/teams/member/"
        response = client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {u'detail': u'Authentication credentials were not provided.'})

        # Get member data
        url = "/api/v1/teams/member/"
        response = client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {u'detail': u'Authentication credentials were not provided.'})

        # Make a user admin
        url = "/api/v1/teams/admin/XPTO/?username=gipmon"
        response = client.put(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {u'detail': u'Authentication credentials were not provided.'})

    def test_teams_errors_duplicated_teams(self):
        user = Account.objects.get(username="gipmon")
        client = APIClient()
        client.force_authenticate(user=user)

        # create a team
        url = "/api/v1/teams/crud/"
        data = {'name': 'TestTeam', 'max_members': 10}
        response = client.post(path=url, data=data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict([('name', u'TestTeam'), ('max_members', 10)]))

        # can not create a team
        url = "/api/v1/teams/crud/"
        data = {'name': 'TestTeam', 'max_members': 10}
        response = client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'status': 'Bad request', 'message': {'name': [u'This field must be unique.']}})

        client.force_authenticate(user=None)

    def test_teams_errors_max_members(self):
        user = Account.objects.get(username="gipmon")
        client = APIClient()
        client.force_authenticate(user=user)

        # create a team
        url = "/api/v1/teams/crud/"
        data = {'name': 'TestTeam', 'max_members': 0}
        response = client.post(path=url, data=data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data,
                         {'status': 'Bad request', 'message':
                             {'max_members': [u'Ensure this value is greater than or equal to 1.']}})

        client.force_authenticate(user=None)

    def test_teams_errors_cant_add_members(self):
        user = Account.objects.get(username="gipmon")
        client = APIClient()
        client.force_authenticate(user=user)

        # create a team
        url = "/api/v1/teams/crud/"
        data = {'name': 'TestTeam', 'max_members': 2}
        response = client.post(path=url, data=data, format='json')

        # add one member to the team
        url = "/api/v1/teams/member/"
        data = {'team_name': 'TestTeam', 'user_name': 'eypo'}
        response = client.post(path=url, data=data, format='json')

        self.assertEqual(response.status_code, 201)
        rsp = dict(response.data)
        del rsp['account']['updated_at']
        del rsp['account']['created_at']

        self.assertEqual(rsp, {'account': OrderedDict(
            [('email', u'ey@rf.pt'), ('username', u'eypo'), ('teaching_institution', u'Universidade de Aveiro'),
             ('first_name', u'Costa'), ('last_name', u'Ferreira'), ('is_staff', False), ('is_superuser', False)]),
                               'is_admin': False, 'team': OrderedDict([('name', u'TestTeam'), ('max_members', 2)])})

        # verify if the user is in the team and is not an admin
        url = "/api/v1/teams/member/TestTeam/?username=eypo"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        rsp = dict(response.data)
        del rsp['account']['updated_at']
        del rsp['account']['created_at']

        self.assertEqual(rsp, {'account': OrderedDict(
            [('email', u'ey@rf.pt'), ('username', u'eypo'), ('teaching_institution', u'Universidade de Aveiro'),
             ('first_name', u'Costa'), ('last_name', u'Ferreira'), ('is_staff', False), ('is_superuser', False)]),
                               'is_admin': False, 'team': OrderedDict([('name', u'TestTeam'), ('max_members', 2)])})

        # can't add another member
        url = "/api/v1/teams/member/"
        data = {'team_name': 'TestTeam', 'user_name': 'eypo94'}
        response = client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data,
                         {'status': 'Bad request', 'message': 'The team reached the max number of members: 2'})

        client.force_authenticate(user=None)
        user = Account.objects.get(username="eypo")
        client = APIClient()
        client.force_authenticate(user=user)

        # add one member to the team
        url = "/api/v1/teams/member/"
        data = {'team_name': 'TestTeam', 'user_name': 'eypo'}
        response = client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {u'detail': u'You do not have permission to perform this action.'})

        # delete the team
        url = "/api/v1/teams/crud/TestTeam/"
        response = client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {u'detail': u'You do not have permission to perform this action.'})

        client.force_authenticate(user=None)

    def test_modify_and_delete(self):
        user = Account.objects.get(username="gipmon")

        bad_user = Account.objects.get(username="eypo")
        client = APIClient()
        client.force_authenticate(user=bad_user)

        # modify
        url = "/api/v1/teams/crud/XPTO/"
        data = {'max_members': 4, 'name': 'XPTO1'}
        response = client.put(path=url, data=data)
        self.assertEqual(response.data, {"detail":"You do not have permission to perform this action."})

        # delete
        url = "/api/v1/teams/crud/XPTO/"
        response = client.delete(path=url)
        self.assertEqual(response.data, {"detail": "You do not have permission to perform this action."})

        # now the god one
        t = TeamMember.objects.get(account=user)
        t.is_admin = True
        t.save()

        client.force_authenticate(user=user)
        # modify
        url = "/api/v1/teams/crud/XPTO/"
        data = {'max_members': 4, 'name': 'XPTO1'}
        response = client.put(path=url, data=data)
        self.assertEqual(response.data, {"status":"Updated","message":"The team has been updated."})

        # delete
        url = "/api/v1/teams/crud/XPTO1/"
        response = client.delete(path=url)
        self.assertEqual(response.data, {"status":"Deleted","message":"The team has been deleted and the team members too."})

    def test_update__admin_member_of_team(self):
        user = Account.objects.get(username="gipmon")

        bad_user = Account.objects.get(username="eypo")
        client = APIClient()
        client.force_authenticate(user=bad_user)

        # modify
        url = "/api/v1/teams/admin/XPTO/?username=gipmon"
        response = client.put(path=url)
        self.assertEqual(response.data, {"detail": "You do not have permission to perform this action."})

    def test_add_and_remove_member_to_team(self):
        user = Account.objects.get(username="gipmon")

        bad_user = Account.objects.get(username="eypo")
        client = APIClient()
        client.force_authenticate(user=bad_user)

        # add new member
        url = "/api/v1/teams/member/"
        data = {'user_name': 'gipmon', 'name': 'XPTO'}
        response = client.post(path=url, data=data)
        self.assertEqual(response.data, {"detail":"You do not have permission to perform this action."})

        # delete new member
        url = "/api/v1/teams/member/XPTO/?username=gipmon"
        response = client.delete(path=url)
        self.assertEqual(response.data, {"detail": "You do not have permission to perform this action."})

    def test_url_slug(self):
        user = Account.objects.get(username="gipmon")
        client = APIClient()
        client.force_authenticate(user=user)

        # create a team slug
        url = "/api/v1/teams/crud/"
        data = {'name': 'Test.Team', 'max_members': 10}
        response = client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, 400)

        # create a team slug
        url = "/api/v1/teams/crud/"
        data = {'name': 'Test*Team', 'max_members': 10}
        response = client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, 400)

        # create a team slug
        url = "/api/v1/teams/crud/"
        data = {'name': 'Test$Team', 'max_members': 10}
        response = client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, 400)

        # create a team slug
        url = "/api/v1/teams/crud/"
        data = {'name': '', 'max_members': -1}
        response = client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, 400)

        client.force_authenticate(user=None)