from django.test import TestCase
from authentication.models import Group, GroupMember, Account


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
