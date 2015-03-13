from django.test import TestCase
from authentication.models import Group, GroupMember, Account

from rest_framework.test import APIClient
from collections import OrderedDict


class GroupsModelsTestCase(TestCase):
    def setUp(self):
        g = Group.objects.create(name="XPTO", max_members=10)
        a1 = Account.objects.create(email="rf@rf.pt", username="gipmon", first_name="Rafael", last_name="Ferreira",
                                    teaching_institution="Universidade de Aveiro")
        a2 = Account.objects.create(email="ey@rf.pt", username="eypo", first_name="Costa", last_name="Ferreira",
                                    teaching_institution="Universidade de Aveiro")
        Account.objects.create(email="af@rf.pt", username="eypo94", first_name="Antonio", last_name="Ferreira",
                               teaching_institution="Universidade de Aveiro")
        GroupMember.objects.create(account=a1, group=g)
        GroupMember.objects.create(account=a2, group=g)

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

    def test_group_details(self):
        group = Group.objects.get(name="XPTO")
        self.assertEqual(group.name, "XPTO")
        self.assertEqual(group.max_members, 10)

    def test_group_members(self):
        a1 = Account.objects.get(username="gipmon")
        a2 = Account.objects.get(username="eypo")

        gm1 = GroupMember.objects.get(account=a1)
        gm2 = GroupMember.objects.get(account=a2)

        self.equal = self.assertEqual(str(gm1), str(a1) + " is in group XPTO (as False)")
        self.assertEqual(str(gm2), str(a2) + " is in group XPTO (as False)")

    def test_groups(self):
        user = Account.objects.get(username="gipmon")
        client = APIClient()
        client.force_authenticate(user=user)

        url = "/api/v1/groups/crud/"

        # only one group is stored
        response = client.get(url)
        self.assertEqual(response.data, [{'name': u'XPTO', 'max_members': 10}])

        # create a group
        data = {'name': 'TestGroup', 'max_members': 10}
        response = client.post(path=url, data=data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict([('name', u'TestGroup'), ('max_members', 10)]))

        # only two groups must be stored
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('name', u'XPTO'), ('max_members', 10)]),
                                         OrderedDict([('name', u'TestGroup'), ('max_members', 10)])])

        # only two groups must be admin
        url = "/api/v1/groups/user_admin/gipmon/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict([('name', u'TestGroup'), ('max_members', 10)])])

        # the user must be administrator of the group
        url = "/api/v1/groups/member/TestGroup/?username=gipmon"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(dict(response.data), {'is_admin': True, 'account': OrderedDict(
            [('id', 1), ('email', u'rf@rf.pt'), ('username', u'gipmon'),
             ('teaching_institution', u'Universidade de Aveiro'), ('first_name', u'Rafael'),
             ('last_name', u'Ferreira')]), 'group': OrderedDict([('name', u'TestGroup'), ('max_members', 10)])})

        # only one member in the group
        url = "/api/v1/groups/members/TestGroup/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        # add one member to the group
        url = "/api/v1/groups/member/"
        data = {'group_name': 'TestGroup', 'user_name': 'eypo'}
        response = client.post(path=url, data=data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(dict(response.data), {'is_admin': False, 'account': OrderedDict(
            [('id', 2), ('email', u'ey@rf.pt'), ('username', u'eypo'),
             ('teaching_institution', u'Universidade de Aveiro'), ('first_name', u'Costa'),
             ('last_name', u'Ferreira')]), 'group': OrderedDict([('name', u'TestGroup'), ('max_members', 10)])})

        # verify if the user is in the group and is not an admin
        url = "/api/v1/groups/member/TestGroup/?username=eypo"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(dict(response.data), {'is_admin': False, 'account': OrderedDict(
            [('id', 2), ('email', u'ey@rf.pt'), ('username', u'eypo'),
             ('teaching_institution', u'Universidade de Aveiro'), ('first_name', u'Costa'),
             ('last_name', u'Ferreira')]), 'group': OrderedDict([('name', u'TestGroup'), ('max_members', 10)])})

        # only two members in the group
        url = "/api/v1/groups/members/TestGroup/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        # make the user a group admin
        url = "/api/v1/groups/admin/TestGroup/?username=eypo"
        response = client.put(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(dict(response.data), {'is_admin': True, 'account': OrderedDict(
            [('id', 2), ('email', u'ey@rf.pt'), ('username', u'eypo'),
             ('teaching_institution', u'Universidade de Aveiro'), ('first_name', u'Costa'),
             ('last_name', u'Ferreira')]), 'group': OrderedDict([('name', u'TestGroup'), ('max_members', 10)])})

        # delete the user from the admins list
        url = "/api/v1/groups/admin/TestGroup/?username=eypo"
        response = client.put(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(dict(response.data), {'is_admin': False, 'account': OrderedDict(
            [('id', 2), ('email', u'ey@rf.pt'), ('username', u'eypo'),
             ('teaching_institution', u'Universidade de Aveiro'), ('first_name', u'Costa'),
             ('last_name', u'Ferreira')]), 'group': OrderedDict([('name', u'TestGroup'), ('max_members', 10)])})

        # delete the user from the grou
        url = "/api/v1/groups/member/TestGroup/?username=eypo"
        response = client.delete(url)
        self.assertEqual(response.status_code, 200)

        # only one member in the group
        url = "/api/v1/groups/members/TestGroup/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        # add the user again
        url = "/api/v1/groups/member/"
        data = {'group_name': 'TestGroup', 'user_name': 'eypo'}
        response = client.post(path=url, data=data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(dict(response.data), {'is_admin': False, 'account': OrderedDict(
            [('id', 2), ('email', u'ey@rf.pt'), ('username', u'eypo'),
             ('teaching_institution', u'Universidade de Aveiro'), ('first_name', u'Costa'),
             ('last_name', u'Ferreira')]), 'group': OrderedDict([('name', u'TestGroup'), ('max_members', 10)])})

        # update the group
        url = "/api/v1/groups/crud/TestGroup/"
        data = {'name': "XPTO2", 'max_members': 10}
        response = client.put(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'status': 'Updated', 'message': 'The group has been updated.'})

        # see if has been updated
        url = "/api/v1/groups/crud/XPTO2/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'max_members': 10, 'name': u'XPTO2'})

        # delete the group
        url = "/api/v1/groups/crud/XPTO2/"
        response = client.delete(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         {'status': 'Deleted', 'message': 'The group has been deleted and the group members too.'})

        # the group not found
        url = "/api/v1/groups/members/XPTO2/"
        response = client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {u'detail': u'Not found'})

        # no GroupMembers instances
        # two from the SetUp
        self.assertEqual(len(GroupMember.objects.all()), 2)

        client.force_authenticate(user=None)

    def test_groups_unauthenticated(self):
        client = APIClient()

        # create a group
        url = "/api/v1/groups/crud/"
        data = {'name': 'TestGroup', 'max_members': 10}
        response = client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {u'detail': u'Authentication credentials were not provided.'})

        # get group details
        url = "/api/v1/groups/crud/XPTO/"
        response = client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {u'detail': u'Authentication credentials were not provided.'})

        # destroy group
        url = "/api/v1/groups/crud/XPTO/"
        response = client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {u'detail': u'Authentication credentials were not provided.'})

        # user groups
        url = "/api/v1/groups/user/gipmon/"
        response = client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {u'detail': u'Authentication credentials were not provided.'})

        # user groups
        url = "/api/v1/groups/members/gipmon/"
        response = client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {u'detail': u'Authentication credentials were not provided.'})

        # Add user to a group
        url = "/api/v1/groups/member/"
        response = client.post(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {u'detail': u'Authentication credentials were not provided.'})

        # Delete an user from a group
        url = "/api/v1/groups/member/"
        response = client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {u'detail': u'Authentication credentials were not provided.'})

        # Get member data
        url = "/api/v1/groups/member/"
        response = client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {u'detail': u'Authentication credentials were not provided.'})

        # Make a user admin
        url = "/api/v1/groups/admin/XPTO/?username=gipmon"
        response = client.put(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {u'detail': u'Authentication credentials were not provided.'})

    def test_groups_errors_duplicated_groups(self):
        user = Account.objects.get(username="gipmon")
        client = APIClient()
        client.force_authenticate(user=user)

        # create a group
        url = "/api/v1/groups/crud/"
        data = {'name': 'TestGroup', 'max_members': 10}
        response = client.post(path=url, data=data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, OrderedDict([('name', u'TestGroup'), ('max_members', 10)]))

        # can not create a group
        url = "/api/v1/groups/crud/"
        data = {'name': 'TestGroup', 'max_members': 10}
        response = client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data,
                         {'status': 'Bad request', 'message': 'The group could not be created with received data.'})

        client.force_authenticate(user=None)

    def test_groups_errors_max_members(self):
        user = Account.objects.get(username="gipmon")
        client = APIClient()
        client.force_authenticate(user=user)

        # create a group
        url = "/api/v1/groups/crud/"
        data = {'name': 'TestGroup', 'max_members': 0}
        response = client.post(path=url, data=data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data,
                         {'status': 'Bad request', 'message': 'The group could not be created with received data.'})

        client.force_authenticate(user=None)

    def test_groups_errors_cant_add_members(self):
        user = Account.objects.get(username="gipmon")
        client = APIClient()
        client.force_authenticate(user=user)

        # create a group
        url = "/api/v1/groups/crud/"
        data = {'name': 'TestGroup', 'max_members': 2}
        response = client.post(path=url, data=data, format='json')

        # add one member to the group
        url = "/api/v1/groups/member/"
        data = {'group_name': 'TestGroup', 'user_name': 'eypo'}
        response = client.post(path=url, data=data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(dict(response.data), {'is_admin': False, 'account': OrderedDict(
            [('id', 2), ('email', u'ey@rf.pt'), ('username', u'eypo'),
             ('teaching_institution', u'Universidade de Aveiro'), ('first_name', u'Costa'),
             ('last_name', u'Ferreira')]), 'group': OrderedDict([('name', u'TestGroup'), ('max_members', 2)])})

        # verify if the user is in the group and is not an admin
        url = "/api/v1/groups/member/TestGroup/?username=eypo"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(dict(response.data), {'is_admin': False, 'account': OrderedDict(
            [('id', 2), ('email', u'ey@rf.pt'), ('username', u'eypo'),
             ('teaching_institution', u'Universidade de Aveiro'), ('first_name', u'Costa'),
             ('last_name', u'Ferreira')]), 'group': OrderedDict([('name', u'TestGroup'), ('max_members', 2)])})

        # can't add another member
        url = "/api/v1/groups/member/"
        data = {'group_name': 'TestGroup', 'user_name': 'eypo94'}
        response = client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data,
                         {'status': 'Bad request', 'message': 'The group reached the number max of members:2'})

        client.force_authenticate(user=None)
        user = Account.objects.get(username="eypo")
        client = APIClient()
        client.force_authenticate(user=user)

        # add one member to the group
        url = "/api/v1/groups/member/"
        data = {'group_name': 'TestGroup', 'user_name': 'eypo'}
        response = client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {u'detail': u'You do not have permission to perform this action.'})

        # delete the group
        url = "/api/v1/groups/crud/TestGroup/"
        response = client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {u'detail': u'You do not have permission to perform this action.'})

        client.force_authenticate(user=None)