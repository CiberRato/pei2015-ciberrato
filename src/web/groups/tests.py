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

        self.assertEqual(str(gm1), str(a1)+" is in group XPTO (as False)")
        self.assertEqual(str(gm2), str(a2)+" is in group XPTO (as False)")

    def test_create_group(self):
        user = Account.objects.get(username="gipmon")
        client = APIClient()
        client.force_authenticate(user=user)

        url = "/api/v1/group/"

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
        self.assertEqual(response.data, [OrderedDict([('name', u'XPTO'), ('max_members', 10)]), OrderedDict([('name', u'TestGroup'), ('max_members', 10)])])

        # the user must be administrator of the group
        url = "/api/v1/group_member/TestGroup/?username=gipmon"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(dict(response.data), {'is_admin': True, 'account': OrderedDict([('id', 1), ('email', u'rf@rf.pt'), ('username', u'gipmon'), ('teaching_institution', u'Universidade de Aveiro'), ('first_name', u'Rafael'), ('last_name', u'Ferreira')]), 'group': OrderedDict([('name', u'TestGroup'), ('max_members', 10)])})

        # only one member in the group
        url = "/api/v1/group_members/TestGroup/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        client.force_authenticate(user=None)
