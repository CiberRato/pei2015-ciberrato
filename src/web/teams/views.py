from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db import transaction

from rest_framework import permissions, viewsets, status, mixins
from rest_framework.response import Response

from authentication.models import Team, TeamMember, Account
from authentication.serializers import AccountSerializer

from teams.permissions import IsAdminOfTeam
from teams.serializers import TeamSerializer, EditTeamSerializer, Member2TeamSerializer, MemberSerializer

from competition.models import Competition


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.order_by('-name')
    serializer_class = TeamSerializer

    def get_permissions(self):
        """
        Any operation is permitted only if the user is Authenticated.
        The create method is permitted only too if the user is Authenticated.
        Note: The create method isn't a SAFE_METHOD
        The others actions (Destroy) is only permitted if the user IsAdminOfTeam
        :return:
        :rtype:
        """
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),
        if self.request.method == 'POST':
            return permissions.IsAuthenticated(),
        return permissions.IsAuthenticated(), IsAdminOfTeam(),

    def create(self, request, **kwargs):
        """
        B{Create} a team and the TeamMember admin by the user that requested the team create method
        B{URL:} ../api/v1/teams/crud/

        :type  name: str
        :param name: The team name
        :type  max_members: number
        :param max_members: max team members
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    g = Team.objects.create(**serializer.validated_data)
                    Competition.create_private_competition(team=g)
                    TeamMember.objects.create(team=g, account=self.request.user, is_admin=True)
            except IntegrityError:
                return Response({'status': 'Bad request',
                                 'message': 'There is a team with that name already!'},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the team attributes by team name
        B{URL:} ../api/v1/teams/crud/<team_name>/

        :type  pk: str
        :param pk: The team name
        """
        team = get_object_or_404(Team.objects.all(), name=kwargs.get('pk'))
        serializer = self.serializer_class(team)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} the team by a team admin user and delete all the team members
        B{URL:} ../api/v1/teams/crud/<team_name>/

        :type  pk: str
        :param pk: The team name
        """
        team = get_object_or_404(Team.objects.all(), name=kwargs.get('pk'))
        team.delete()
        return Response({'status': 'Deleted',
                         'message': 'The team has been deleted and the team members too.'},
                        status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        B{Update} the team
        B{URL:} ../api/v1/teams/crud/<team_name>/

        :type  pk: str
        :param pk: The team name
        """
        team = get_object_or_404(Team.objects.all(), name=kwargs.get('pk'))
        serializer = EditTeamSerializer(data=request.data)

        if serializer.is_valid():
            team.max_members = serializer.validated_data['max_members']
            team.name = serializer.validated_data['name']
            team.save()
            return Response({'status': 'Updated',
                             'message': 'The team has been updated.'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'status': 'Bad request',
                             'message': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)


class AccountTeamsViewSet(mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    queryset = Account.objects.all()
    serializer_class = TeamSerializer

    def get_permissions(self):
        """
        If an user wants to see the teams of another user it must be Authenticated.
        :return: True if Authenticated or False if not
        :rtype: permissions.isAuthenticated()
        """
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the teams of an Account
        B{URL:} ../api/v1/teams/user/<username>/
        """
        self.queryset = self.queryset.get(username=kwargs.get('pk'))
        serializer = self.serializer_class(self.queryset.teams, many=True)
        return Response(serializer.data)


class AccountTeamsAdminViewSet(mixins.RetrieveModelMixin,
                               viewsets.GenericViewSet):
    queryset = Account.objects.all()
    serializer_class = TeamSerializer

    def get_permissions(self):
        """
        If an user wants to see the teams admin of another user it must be Authenticated.
        :return: True if Authenticated or False if not
        :rtype: permissions.isAuthenticated()
        """
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the teams where the user is admin
        B{URL:} ../api/v1/teams/user_admin/<username>/
        """
        self.queryset = self.queryset.get(username=kwargs.get('pk'))
        teams = []
        for team in self.queryset.teams.all():
            gm = TeamMember.objects.get(account=self.queryset, team=team)
            if gm.is_admin:
                teams += [team]

        serializer = self.serializer_class(teams, many=True)
        return Response(serializer.data)


class TeamMembersViewSet(mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    queryset = TeamMember.objects.all()
    serializer_class = AccountSerializer

    def get_permissions(self):
        """
        If one user wants to see the team members list of one team it must be Authenticated.
        :return: True if Authenticated or False if not
        :rtype: permissions.isAuthenticated()
        """
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the Team members list
        B{URL:} ../api/v1/teams/members/<team_name>/
        """
        team = get_object_or_404(Team.objects.all(), name=kwargs.get('pk'))
        queryset = [gm.account for gm in team.teammember_set.all()]
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class MemberInTeamViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                          mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Team.objects.all()
    serializer_class = Member2TeamSerializer

    def get_permissions(self):
        """
        If one user wants to add one user to the team it must be a Admin of the team.
        If one user wants to remove other user from the team it must be a admin of the team.
        The others methods: retrieve it must be only Authenticated.
        """
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),
        return permissions.IsAuthenticated(), IsAdminOfTeam(),

    def create(self, request, **kwargs):
        """
        B{Create} a TeamMember to a Team
        B{URL:} ../api/v1/teams/member/

        :type  user_name: str
        :param user_name: The user name
        :type  team_name: str
        :param team_name: The team name
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            team = get_object_or_404(Team.objects.all(), name=serializer.validated_data['team_name'])
            user = get_object_or_404(Account.objects.all(), username=serializer.validated_data['user_name'])

            number_of_members = len(team.teammember_set.all())
            if number_of_members >= team.max_members:
                return Response({'status': 'Bad request',
                                 'message': 'The team reached the max number of members: ' + str(number_of_members)},
                                status=status.HTTP_400_BAD_REQUEST)
            try:
                with transaction.atomic():
                    team_member = TeamMember.objects.create(team=team, account=user)
                    team_member_serializer = MemberSerializer(team_member)
                    return Response(team_member_serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({'status': 'Bad request',
                                 'message': 'The user is already in the team'},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response({'status': 'Bad request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} a TeamMember from a Team
        B{URL:} ../api/v1/teams/member/<team_name>/?username=<user_name>

        :type  user_name: str
        :param user_name: The user name
        :type  team_name: str
        :param team_name: The team name
        """
        if 'username' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?username=*username*'},
                            status=status.HTTP_400_BAD_REQUEST)

        team = get_object_or_404(Team.objects.all(), name=kwargs.get('pk'))
        user = get_object_or_404(Account.objects.all(), username=request.GET.get('username', ''))

        member_not_in_team = (len(TeamMember.objects.filter(team=team, account=user)) == 0)

        if member_not_in_team:
            return Response({'status': 'Bad request',
                             'message': 'The user is not in the team'},
                            status=status.HTTP_400_BAD_REQUEST)

        team_member = TeamMember.objects.get(team=team, account=user)
        team_member.delete()

        if len(team.teammember_set.all()) == 0:
            team = get_object_or_404(Team.objects.all(), name=kwargs.get('pk'))
            team.delete()

        return Response(status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the TeamMember of a Team
        B{URL:} ../api/v1/teams/member/<team_name>/?username=<user_name>

        :type  user_name: str
        :param user_name: The user name
        :type  team_name: str
        :param team_name: The team name
        """
        if 'username' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?username=*username*'},
                            status=status.HTTP_400_BAD_REQUEST)

        team = get_object_or_404(Team.objects.all(), name=kwargs.get('pk'))
        user = get_object_or_404(Account.objects.all(), username=request.GET.get('username', ''))

        member_not_in_team = (len(TeamMember.objects.filter(team=team, account=user)) == 0)

        if member_not_in_team:
            return Response({'status': 'Bad request',
                             'message': 'The user is not in the team'},
                            status=status.HTTP_400_BAD_REQUEST)

        team_member = TeamMember.objects.get(team=team, account=user)
        team_member_serializer = MemberSerializer(team_member)

        return Response(team_member_serializer.data, status=status.HTTP_200_OK)


class MakeMemberAdminViewSet(mixins.UpdateModelMixin,
                             viewsets.GenericViewSet):
    queryset = Team.objects.all()
    serializer_class = MemberSerializer

    def get_permissions(self):
        """
        If one user wants to add one user to the admin list of the team it must be a Admin of the team.
        If one user wants to remove other user from the admin list of team it must be a admin of the team.
        The others methods: retrieve it must be only Authenticated.
        """
        return permissions.IsAuthenticated(), IsAdminOfTeam(),

    def update(self, request, *args, **kwargs):
        """
        B{Update}: make admin of the Team
        B{URL:} ../api/v1/teams/admin/<team_name>/?username=<user_name>

        :type  username: str
        :param username: The user name
        :type  pk: str
        :param pk: The team name
        """
        if 'username' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?username=*username*'},
                            status=status.HTTP_400_BAD_REQUEST)

        team = get_object_or_404(Team.objects.all(), name=kwargs.get('pk'))
        user = get_object_or_404(Account.objects.all(), username=request.GET.get('username', ''))

        member_not_in_team = (len(TeamMember.objects.filter(team=team, account=user)) == 0)

        if member_not_in_team:
            return Response({'status': 'Bad request',
                             'message': 'The user is not in the team'},
                            status=status.HTTP_400_BAD_REQUEST)

        num_admins = 0
        for member in team.teammember_set.all():
            if member.is_admin:
                num_admins += 1

        team_member = TeamMember.objects.get(team=team, account=user)

        if team_member.is_admin and num_admins == 1:
            return Response({'status': 'Bad request',
                             'message': 'The team mast have at least one admin!'},
                            status=status.HTTP_400_BAD_REQUEST)

        team_member.is_admin = not team_member.is_admin
        team_member.save()

        team_member_serializer = MemberSerializer(team_member)

        return Response(team_member_serializer.data, status=status.HTTP_200_OK)