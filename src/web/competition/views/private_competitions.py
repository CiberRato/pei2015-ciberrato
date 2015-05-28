import uuid

from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db import transaction
from django.conf import settings

from django.core.files.storage import default_storage
from rest_framework import permissions
from rest_framework import viewsets, status, mixins, views
from rest_framework.response import Response

import requests

from .simplex import TrialSimplex
from ..permissions import MustBePrivateCompetition, UserCanAccessToThePrivateCompetition
from ..serializers import PrivateCompetitionSerializer, PrivateRoundSerializer, \
    InputPrivateRoundSerializer, TrialSerializer, PrivateRoundTrialsSerializer
from ..models import Competition, TeamEnrolled, AgentGrid, Round, Trial, \
    CompetitionAgent, LogTrialAgent


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

        > Permissions
        # The competition must be one private competition
        # The team must be enrolled in the competition, if yes the team can be in the competition
        """
        private_competition = Competition.objects.get(name=kwargs.get('pk'))

        # this competition must be a private competition
        MustBePrivateCompetition(competition=private_competition)

        # verify if the team is enrolled in the competition
        UserCanAccessToThePrivateCompetition(competition=private_competition, user=request.user)

        # get round for this competition
        rounds = Round.objects.filter(parent_competition=private_competition)
        serializer = self.serializer_class(rounds, many=True)

        return Response(serializer.data)


class PrivateCompetitionRound(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                              mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = InputPrivateRoundSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def create(self, request, *args, **kwargs):
        """
        B{Create} a private competition round
        B{URL:} ../api/v1/competitions/private/round/

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
            MustBePrivateCompetition(competition=private_competition)

            # verify if the team is enrolled in the competition
            UserCanAccessToThePrivateCompetition(competition=private_competition, user=request.user)

            # create a round for this competition
            try:
                has = Round.objects.filter(parent_competition=private_competition,
                                           grid_path=default_storage.path(serializer.validated_data['grid']),
                                           param_list_path=default_storage.path(
                                               serializer.validated_data['param_list']),
                                           lab_path=default_storage.path(serializer.validated_data['lab'])).count()

                if has > 0:
                    return Response({'status': 'Bad request',
                                     'message': 'You already have one solo trial with those files!'},
                                    status=status.HTTP_400_BAD_REQUEST)

                with transaction.atomic():
                    r = Round.objects.create(name=uuid.uuid4(), parent_competition=private_competition)
                    PrivateCompetitionRound.set_param(r, serializer.validated_data['grid'], 'grid')
                    PrivateCompetitionRound.set_param(r, serializer.validated_data['param_list'], 'param_list')
                    PrivateCompetitionRound.set_param(r, serializer.validated_data['lab'], 'lab')
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

    def retrieve(self, request, *args, **kwargs):
        """
        B{List} the trials for one round and the file list
        B{URL:} ../api/v1/competitions/private/round/<round_name>/
        """
        # the round must exist
        r = Round.objects.get(name=kwargs.get('pk'))

        # the parent competition of the round must be private competition
        MustBePrivateCompetition(competition=r.parent_competition)

        # the team must be enrolled in the parent competition
        UserCanAccessToThePrivateCompetition(competition=r.parent_competition, user=request.user)

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
        serializer = PrivateRoundTrialsSerializer(private_round)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} the round
        B{URL:} ../api/v1/competitions/private/round/<round_name>/
        """
        # the round must exist
        r = Round.objects.get(name=kwargs.get('pk'))

        # the parent competition of the round must be private competition
        MustBePrivateCompetition(competition=r.parent_competition)

        # the team must be enrolled in the parent competition
        UserCanAccessToThePrivateCompetition(competition=r.parent_competition, user=request.user)

        r.delete()

        return Response({'status': 'Deleted',
                         'message': 'The solo trials had been deleted!'},
                        status=status.HTTP_200_OK)


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
        MustBePrivateCompetition(competition=r.parent_competition)

        # verify if the teams owns it
        UserCanAccessToThePrivateCompetition(competition=r.parent_competition, user=request.user)

        # get team grid position for this competition
        grid_position = r.parent_competition.gridpositions_set.first()

        # the grid must have at least one agent
        if grid_position.agentgrid_set.count() == 0:
            return Response({'status': 'Bad request',
                             'message': 'Please select your agents to run this trial in the first page of Solo Trials!'},
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
                    try:
                        competition_agent = CompetitionAgent.objects.get(
                            competition=trial.round.parent_competition,
                            agent=agent_grid.agent,
                            round=trial.round)
                    except CompetitionAgent.DoesNotExist:
                        competition_agent = CompetitionAgent.objects.create(
                            competition=trial.round.parent_competition,
                            agent=agent_grid.agent,
                            round=trial.round)
                    try:
                        LogTrialAgent.objects.create(competition_agent=competition_agent,
                                                     trial=trial,
                                                     pos=pos)
                    except IntegrityError:
                        pass

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


class SoloTrial(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Trial.objects.all()
    serializer_class = TrialSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} the trial
        B{URL:} ../api/v1/competitions/private/trial/<trial_identifier>/
        """
        # the round must exist
        trial = Trial.objects.get(identifier=kwargs.get('pk'))

        # the parent competition of the round must be private competition
        MustBePrivateCompetition(competition=trial.round.parent_competition)

        # the team must be enrolled in the parent competition
        UserCanAccessToThePrivateCompetition(competition=trial.round.parent_competition, user=request.user)

        trial.delete()

        return Response({'status': 'Deleted',
                         'message': 'The solo trial has been deleted!'},
                        status=status.HTTP_200_OK)