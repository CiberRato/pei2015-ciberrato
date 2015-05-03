from django.shortcuts import get_object_or_404
from django.db import IntegrityError
import uuid
from django.db import transaction
from django.conf import settings
from django.core.files.storage import default_storage

from rest_framework import permissions
from rest_framework import viewsets, status, mixins, views
from rest_framework.response import Response

import requests

from authentication.models import Team, TeamMember

from .simplex import GridPositionsSimplex, AgentGridSimplex
from ..models import Competition, GridPositions, TeamEnrolled, AgentGrid, Agent, TrialGrid, Round, Trial,\
    CompetitionAgent, LogTrialAgent
from ..serializers import CompetitionSerializer, PrivateCompetitionSerializer, PrivateRoundSerializer, \
    InputPrivateRoundSerializer, TrialSerializer, PrivateRoundTrialsSerializer
from .simplex import TrialSimplex
from ..permissions import IsStaff
from authentication.models import Account


class PrivateCompetitionsUser(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = PrivateCompetitionSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def list(self, request, *args, **kwargs):
        """
        B{List} user private competitions
        B{URL:} ../api/v1/competitions/private/list/
        """
        private_competitions_team_enrolled = []

        for team in request.user.teams.all():
            for team_enrolled in team.teamenrolled_set.all():
                if team_enrolled.competition.type_of_competition.name == settings.PRIVATE_COMPETITIONS_NAME:
                    private_competitions_team_enrolled += [team_enrolled]

        serializer = self.serializer_class(private_competitions_team_enrolled, many=True)

        return Response(serializer.data)


class PrivateCompetitionsRounds(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = PrivateRoundSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{List} private competition rounds
        B{URL:} ../api/v1/competitions/private/rounds/<competition_name>/
        """
        private_competition = Competition.objects.get(name=kwargs.get('pk'))

        # this competition must be a private competition
        if private_competition.type_of_competition.name != settings.PRIVATE_COMPETITIONS_NAME:
            return Response({'status': 'Bad request',
                             'message': 'You can only see this for private competitions!'},
                            status=status.HTTP_400_BAD_REQUEST)

        # verify if the team is enrolled in the competition
        team_enrolled = TeamEnrolled.objects.filter(competition=private_competition).first()
        if team_enrolled.team not in request.user.teams.all():
            return Response({'status': 'Bad request',
                             'message': 'You can not see the rounds for this competition!'},
                            status=status.HTTP_400_BAD_REQUEST)

        # get round for this competition
        rounds = Round.objects.filter(parent_competition=private_competition)
        serializer = self.serializer_class(rounds, many=True)

        return Response(serializer.data)


class CreatePrivateCompetitionRound(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = InputPrivateRoundSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def create(self, request, *args, **kwargs):
        """
        B{Create} a private competition round
        B{URL:} ../api/v1/competitions/private/create_round/

        :type  competition_name: str
        :param competition_name: The competition name
        :type  grid: str
        :param grid: The grid path from resources
        :type  param_list: str
        :param param_list: The param_list from resources
        :type  lab: str
        :param lab: The lab from resources
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            private_competition = get_object_or_404(Competition.objects.all(),
                                                    name=serializer.validated_data['competition_name'])

            # this competition must be a private competition
            if private_competition.type_of_competition.name != settings.PRIVATE_COMPETITIONS_NAME:
                return Response({'status': 'Bad request',
                                 'message': 'You can only see this for private competitions!'},
                                status=status.HTTP_400_BAD_REQUEST)

            # verify if the team is enrolled in the competition
            team_enrolled = TeamEnrolled.objects.filter(competition=private_competition).first()
            if team_enrolled.team not in request.user.teams.all():
                return Response({'status': 'Bad request',
                                 'message': 'You can not see the rounds for this competition!'},
                                status=status.HTTP_400_BAD_REQUEST)

            # create a round for this competition
            try:
                has = Round.objects.filter(parent_competition=private_competition,
                                           grid_path=default_storage.path(serializer.validated_data['grid']),
                                           param_list_path=default_storage.path(serializer.validated_data['param_list']),
                                           lab_path=default_storage.path(serializer.validated_data['lab'])).count()

                if has > 0:
                    return Response({'status': 'Bad request',
                                     'message': 'You already have one round with those files!'},
                                    status=status.HTTP_400_BAD_REQUEST)

                with transaction.atomic():
                    r = Round.objects.create(name=uuid.uuid4(), parent_competition=private_competition)
                    CreatePrivateCompetitionRound.set_param(r, serializer.validated_data['grid'], 'grid')
                    CreatePrivateCompetitionRound.set_param(r, serializer.validated_data['param_list'], 'param_list')
                    CreatePrivateCompetitionRound.set_param(r, serializer.validated_data['lab'], 'lab')
            except IntegrityError, e:
                return Response({'status': 'Bad request',
                                 'message': e.message},
                                status=status.HTTP_400_BAD_REQUEST)

            serializer = PrivateRoundSerializer(r)
            return Response(serializer.data)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def set_param(r, path, param):
        if not default_storage.exists(path):
            raise IntegrityError('The file doesn\'t exists!')

        # verify if is a valid path
        if not path.startswith('resources/'):
            raise IntegrityError('Invalid file!')

        setattr(r, param + "_path", default_storage.path(path))
        setattr(r, param + "_can_delete", False)
        r.save()


class GetRoundTrials(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Round.objects.all()
    serializer_class = PrivateRoundTrialsSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        B{List} the trials for one round and the file list
        B{URL:} ../api/v1/competitions/private/round/<round_name>/
        """
        # the round must exist
        r = Round.objects.get(name=kwargs.get('pk'))

        # the parent competition of the round must be private competition
        if r.parent_competition.type_of_competition.name != settings.PRIVATE_COMPETITIONS_NAME:
            return Response({'status': 'Bad request',
                             'message': 'You can only see this for private competitions!'},
                            status=status.HTTP_400_BAD_REQUEST)

        # the team must be enrolled in the parent competition
        team_enrolled = TeamEnrolled.objects.filter(competition=r.parent_competition).first()
        if team_enrolled.team not in request.user.teams.all():
            return Response({'status': 'Bad request',
                             'message': 'You can not see the rounds for this competition!'},
                            status=status.HTTP_400_BAD_REQUEST)

        # get the trials
        trials = Trial.objects.filter(round=r)
        trials = [TrialSimplex(trial) for trial in trials]

        class PrivateRoundTrials:
            def __init__(self, rnd, trials_simplex):
                serial = PrivateRoundSerializer(rnd)
                self.round = serial.data
                serial = TrialSerializer(trials_simplex, many=True)
                self.trials = serial.data

        # join the trials with the files name
        private_round = PrivateRoundTrials(r, trials)

        # serializer
        serializer = self.serializer_class(private_round)

        return Response(serializer.data)


class RunPrivateTrial(views.APIView):
    def get_permissions(self):
        return permissions.IsAuthenticated(),

    @staticmethod
    def post(request):
        """
        B{Launch} one trial for that round
        B{URL:} ../api/v1/competitions/private/launch_trial/
        """
        # get round
        r = get_object_or_404(Round.objects.all(), name=request.data.get('round_name', ''))

        # verify if the round is from a private competition
        if r.parent_competition.type_of_competition.name != settings.PRIVATE_COMPETITIONS_NAME:
            return Response({'status': 'Bad request',
                             'message': 'You can only see this for private competitions!'},
                            status=status.HTTP_400_BAD_REQUEST)

        # verify if the teams owns it
        team_enrolled = TeamEnrolled.objects.filter(competition=r.parent_competition).first()
        if team_enrolled.team not in request.user.teams.all():
            return Response({'status': 'Bad request',
                             'message': 'You can not see the rounds for this competition!'},
                            status=status.HTTP_400_BAD_REQUEST)

        # get team grid position for this competition
        grid_position = r.parent_competition.gridpositions_set.first()

        # the grid must have at least one agent
        if grid_position.agentgrid_set.count() == 0:
            return Response({'status': 'Bad request',
                             'message': 'The grid must have at least one agent!'},
                            status=status.HTTP_400_BAD_REQUEST)

        # create trial for this round
        trial = Trial.objects.create(round=r)

        # same method used in the prepare
        agents_grid = AgentGrid.objects.filter(grid_position=grid_position)

        pos = 1
        for agent_grid in agents_grid:
            if agent_grid.agent.code_valid:
                team_enroll = TeamEnrolled.objects.get(team=agent_grid.agent.team,
                                                       competition=trial.round.parent_competition)
                if team_enroll.valid:
                    # competition agent
                    competition_agent_not_exists = (len(CompetitionAgent.objects.filter(
                        competition=trial.round.parent_competition,
                        agent=agent_grid.agent,
                        round=trial.round)) == 0)

                    if competition_agent_not_exists:
                        competition_agent = CompetitionAgent.objects.create(
                            competition=trial.round.parent_competition,
                            agent=agent_grid.agent,
                            round=trial.round)
                    else:
                        competition_agent = CompetitionAgent.objects.get(
                            competition=trial.round.parent_competition,
                            agent=agent_grid.agent,
                            round=trial.round)

                    log_sim_agent_not_exists = (len(LogTrialAgent.objects.filter(
                        competition_agent=competition_agent,
                        trial=trial,
                        pos=pos)) == 0)

                    # log trial agent
                    if log_sim_agent_not_exists:
                        LogTrialAgent.objects.create(competition_agent=competition_agent,
                                                     trial=trial,
                                                     pos=pos)

                    pos += 1

        params = {'trial_identifier': trial.identifier}

        try:
            requests.post(settings.PREPARE_SIM_ENDPOINT, params)
        except requests.ConnectionError:
            return Response({'status': 'Bad Request',
                             'message': 'The simulator appears to be down!'},
                            status=status.HTTP_400_BAD_REQUEST)

        trial.waiting = True
        trial.prepare = False
        trial.started = False
        trial.save()

        return Response({'status': 'Trial started',
                         'message': 'The solo trial has been launched!'},
                        status=status.HTTP_200_OK)