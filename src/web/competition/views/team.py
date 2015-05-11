from django.shortcuts import get_object_or_404, get_list_or_404
from django.db import IntegrityError
from django.db import transaction
from django.conf import settings

from rest_framework import permissions
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response

from teams.serializers import TeamSerializer
from teams.permissions import IsAdminOfTeam

from ..permissions import IsStaff
from .simplex import RoundSimplex, TeamEnrolledSimplex
from ..models import Competition, Round, TeamEnrolled, Agent
from ..serializers import RoundSerializer, TeamEnrolledSerializer, TeamEnrolledOutputSerializer, \
    CompetitionSerializer

from authentication.models import Team
from authentication.models import Account

from notifications.models import NotificationBroadcast, NotificationTeam


class CompetitionGetTeamsViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = TeamEnrolledOutputSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the list of a Teams enrolled and with valid inscription or not in the Competition
        B{URL:} ../api/v1/competitions/teams/<competition_name>/

        :type  competition_name: str
        :param competition_name: The competition name
        """
        competition = get_object_or_404(self.queryset, name=kwargs.get('pk'))

        if competition.type_of_competition.name == settings.PRIVATE_COMPETITIONS_NAME:
            if competition.teamenrolled_set.first().team not in request.user.teams.all():
                return Response({'status': 'Bad request',
                                 'message': 'You can not see the rounds for this competition!'},
                                status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(competition.teamenrolled_set.all(), many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class MyEnrolledTeamsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = TeamEnrolledSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def list(self, request, *args, **kwargs):
        """
        B{Retrieve} the list of a Teams enrolled
        B{URL:} ../api/v1/competitions/my_enrolled_teams/
        """
        enrolled_teams = []
        for team in request.user.teams.all():
            for eg in team.teamenrolled_set.all():
                if eg.competition.type_of_competition.name != settings.PRIVATE_COMPETITIONS_NAME:
                    enrolled_teams += [TeamEnrolledSimplex(eg)]

        serializer = self.serializer_class(enrolled_teams, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CompetitionGetNotValidTeamsViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = TeamSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the list of a Teams enrolled with inscription not valid in the Competition
        B{URL:} ../api/v1/competitions/teams_not_valid/<competition_name>/

        :type  competition_name: str
        :param competition_name: The competition name
        """
        competition = get_object_or_404(self.queryset, name=kwargs.get('pk'))

        if competition.type_of_competition.name == settings.PRIVATE_COMPETITIONS_NAME:
            return Response({'status': 'Bad Request',
                             'message': 'This competition can\'t be seen!'},
                            status=status.HTTP_400_BAD_REQUEST)

        not_valid = TeamEnrolled.objects.filter(valid=False, competition=competition)
        not_valid_teams = [g.team for g in not_valid]
        serializer = self.serializer_class(not_valid_teams, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CompetitionOldestRoundViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = RoundSerializer
    queryset = Round.objects.all()

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the oldest round competition
        B{URL:} ../api/v1/competitions/first_round/<competition_name>/

        :type  competition_name: str
        :param competition_name: The competition name
        """
        competition = get_object_or_404(Competition.objects.all(), name=kwargs.get('pk'))

        if competition.type_of_competition.name == settings.PRIVATE_COMPETITIONS_NAME:
            return Response({'status': 'Bad Request',
                             'message': 'This competition can\'t be seen!'},
                            status=status.HTTP_400_BAD_REQUEST)

        if len(competition.round_set.all()) == 0:
            return Response({'status': 'Bad request',
                             'message': 'Not found '},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(RoundSimplex(competition.round_set.all().reverse()[0]))

        return Response(serializer.data, status=status.HTTP_200_OK)


class CompetitionEarliestRoundViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = RoundSerializer
    queryset = Round.objects.all()

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the earliest round competition
        B{URL:} ../api/v1/competitions/earliest_round/<competition_name>/

        :type  competition_name: str
        :param competition_name: The competition name
        """
        competition = get_object_or_404(Competition.objects.all(), name=kwargs.get('pk'))

        if competition.type_of_competition.name == settings.PRIVATE_COMPETITIONS_NAME:
            return Response({'status': 'Bad Request',
                             'message': 'This competition can\'t be seen!'},
                            status=status.HTTP_400_BAD_REQUEST)

        if len(competition.round_set.all()) == 0:
            return Response({'status': 'Bad request',
                             'message': 'Not found '},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(RoundSimplex(competition.round_set.all()[0]))

        return Response(serializer.data, status=status.HTTP_200_OK)


class ToggleTeamValid(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = TeamEnrolled.objects.all()
    serializer_class = TeamEnrolledSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(), IsStaff(),

    def create(self, request, *args, **kwargs):
        """
        B{Toggle} the Team Enrolled inscription
        B{URL:} ../api/v1/competitions/toggle_team_inscription/

        :type  competition_name: str
        :param competition_name: The Competition name
        :type  team_name: str
        :param team_name: The Team name
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            competition = get_object_or_404(Competition.objects.all(),
                                            name=serializer.validated_data['competition_name'])

            if competition.type_of_competition.name == settings.PRIVATE_COMPETITIONS_NAME:
                return Response({'status': 'Bad Request',
                                 'message': 'This competition can\'t be seen!'},
                                status=status.HTTP_400_BAD_REQUEST)

            team = get_object_or_404(Team.objects.all(), name=serializer.validated_data['team_name'])
            team_enrolled = get_object_or_404(TeamEnrolled.objects.all(), competition=competition, team=team)
            team_enrolled.valid = not team_enrolled.valid
            team_enrolled.save()

            if team_enrolled.valid:
                NotificationTeam.add(team=team, status="ok",
                                     message="Your inscription is the competition " + competition.name
                                             + " is now valid!")
                NotificationTeam.add(team=team, status="info",
                                     message="Do not forget to create one grid position for this competition!")
            else:
                NotificationTeam.add(team=team, status="error",
                                     message="Your inscription is the competition " + competition.name
                                             + " is now not valid!")

            return Response({'status': 'Inscription toggled!',
                             'message': 'Inscription is now: ' + str(team_enrolled.valid)},
                            status=status.HTTP_200_OK)

        return Response({'status': 'Bad request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class MyEnrolledTeamsInCompetitionViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = TeamEnrolledSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the list of a Teams enrolled by username and competition
        B{URL:} ../api/v1/competitions/my_enrolled_teams_competition/<username>/?competition_name=<competition_name>

        :type  username: str
        :param username: The username
        :type  competition_name: str
        :param competition_name: The competition name
        """
        user = get_object_or_404(Account.objects.all(), username=kwargs.get('pk'))
        competition = get_object_or_404(Competition.objects.all(), name=request.GET.get('competition_name', ''))

        enrolled_teams = []
        for team in user.teams.all():
            enrolled_team = TeamEnrolled.objects.filter(team=team, competition=competition)
            if len(enrolled_team) == 1:
                enrolled_teams += [TeamEnrolledSimplex(enrolled_team[0])]

        serializer = self.serializer_class(enrolled_teams, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class GetEnrolledTeamCompetitionsViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the list of competitions enrolled and with valid inscription by team
        B{URL:} ../api/v1/competitions/team_enrolled_competitions/<team_name>/

        :type  team_name: str
        :param team_name: The team name
        """
        team = get_object_or_404(Team.objects.all(), name=kwargs.get('pk'))
        teams = TeamEnrolled.objects.filter(team=team, valid=True)

        competitions = []
        for team_enrolled in teams:
            if team_enrolled.competition.type_of_competition.name != settings.PRIVATE_COMPETITIONS_NAME:
                competitions += [team_enrolled.competition]

        serializer = self.serializer_class(competitions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class EnrollTeam(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                 mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = TeamEnrolled.objects.all()
    serializer_class = TeamEnrolledSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),
        return permissions.IsAuthenticated(), IsAdminOfTeam(),

    def list(self, request, **kwargs):
        """
        B{List} the enrolled teams
        B{URL:} ../api/v1/competitions/enroll/
        """
        serializer = self.serializer_class([TeamEnrolledSimplex(ge=query) for query in TeamEnrolled.objects.all()],
                                           many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the valid inscriptions in one competition for the team
        B{URL:} ../api/v1/competitions/enroll/<team_name>/

        :type  competition_name: str
        :param competition_name: The Competition name
        :type  team_name: str
        :param team_name: The Team name
        """
        team = get_object_or_404(Team.objects.all(), name=kwargs.get('pk'))
        team_enrolled = get_list_or_404(TeamEnrolled.objects.all(), team=team, valid=True)
        serializer = self.serializer_class([TeamEnrolledSimplex(team) for team in team_enrolled], many=True)
        return Response(serializer.data)

    def create(self, request, **kwargs):
        """
        B{Create} a Team Enrolled to a competition
        B{URL:} ../api/v1/competitions/enroll/

        :type  competition_name: str
        :param competition_name: The Competition name
        :type  team_name: str
        :param team_name: The Team name
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            competition = get_object_or_404(Competition.objects.all(),
                                            name=serializer.validated_data['competition_name'])
            team = get_object_or_404(Team.objects.all(), name=serializer.validated_data['team_name'])

            if competition.state_of_competition != "Register":
                return Response({'status': 'Not allowed',
                                 'message': 'The team can\'t enroll in the competition.'},
                                status=status.HTTP_401_UNAUTHORIZED)
            try:
                with transaction.atomic():
                    TeamEnrolled.objects.create(competition=competition, team=team)
            except IntegrityError:
                return Response({'status': 'Bad request',
                                 'message': 'The team already enrolled.'},
                                status=status.HTTP_400_BAD_REQUEST)

            # if the competition allow remote agents let's create a remote agent for the team
            if competition.type_of_competition.allow_remote_agents:
                if Agent.objects.filter(agent_name="Remote", is_remote=True, team=team).count() == 0:
                    try:
                        with transaction.atomic():
                            Agent.objects.create(agent_name="Remote", user=request.user, is_remote=True, team=team,
                                                 code_valid=True, language="Unknown")
                    except IntegrityError:
                        pass

            # send notification to admin
            NotificationBroadcast.add(channel="admin", status="ok",
                                      message="The team " + team.name + " has enrolled in the competition " +
                                              competition.name + "!")

            return Response({'status': 'Created',
                             'message': 'The team has enrolled.'},
                            status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class AdminEnrollTeam(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = TeamEnrolled.objects.all()
    serializer_class = TeamEnrolledSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),
        return permissions.IsAuthenticated(), IsStaff(),

    def destroy(self, request, *args, **kwargs):
        """
        B{Remove} a team from the competition
        B{URL:} ../api/v1/competitions/remove_enroll_team/<competition_name>/?team_name=<team_name>

        :type  competition_name: str
        :param competition_name: The competition name
        :type  team_name: str
        :param team_name: The team name
        """
        if 'team_name' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?team_name=*team_name*'},
                            status=status.HTTP_400_BAD_REQUEST)

        competition = get_object_or_404(Competition.objects.all(), name=kwargs.get('pk'))

        if competition.type_of_competition.name == settings.PRIVATE_COMPETITIONS_NAME:
            return Response({'status': 'Bad Request',
                             'message': 'This grid can\'t be seen!'},
                            status=status.HTTP_400_BAD_REQUEST)

        team = get_object_or_404(Team.objects.all(), name=request.GET.get('team_name', ''))

        team_not_enrolled = (len(TeamEnrolled.objects.filter(competition=competition, team=team)) == 0)

        if team_not_enrolled:
            return Response({'status': 'Bad request',
                             'message': 'The team is not enrolled in the competition.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # validations update values
        competition = get_object_or_404(Competition.objects.all(), name=kwargs.get('pk'))
        team = get_object_or_404(Team.objects.all(), name=request.GET.get('team_name', ''))

        team_enrolled = TeamEnrolled.objects.get(competition=competition, team=team)
        team_enrolled.delete()

        return Response(status=status.HTTP_200_OK)