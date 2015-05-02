from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db import IntegrityError
from django.db import transaction

import requests

from rest_framework import permissions
from rest_framework import mixins, viewsets, status, views
from rest_framework.response import Response

from agent.models import Agent

from .simplex import TrialSimplex, TrialAgentSimplex, TrialGridSimplex
from ..serializers import TrialSerializer, TrialAgentSerializer, TrialGridsSerializer, \
    TrialGridInputSerializer
from ..models import Competition, Round, Trial, CompetitionAgent, LogTrialAgent, TrialGrid, \
    GridPositions, TeamEnrolled, AgentGrid
from ..shortcuts import *
from ..permissions import IsStaff

from authentication.models import Team
from notifications.models import NotificationBroadcast


class TrialViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                   mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Trial.objects.all()
    serializer_class = TrialSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),
        return permissions.IsAuthenticated(), IsStaff(),

    def create(self, request, *args, **kwargs):
        """
        B{Create} one trial for one round
        B{URL:} ../api/v1/competitions/trial/

        :type  round_name: str
        :param round_name: The round name
        :type  competition_name: str
        :param competition_name: The competition name
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            competition = get_object_or_404(Competition.objects.all(), name=serializer.validated_data['competition_name'])

            if competition.type_of_competition.name == settings.PRIVATE_COMPETITIONS_NAME:
                return Response({'status': 'Bad Request',
                                 'message': 'This grid can\'t be seen!'},
                                status=status.HTTP_400_BAD_REQUEST)

            r = get_object_or_404(Round.objects.all(), name=serializer.validated_data['round_name'],
                                  parent_competition=competition)

            if not bool(r.grid_path) or not bool(r.param_list_path) or not bool(r.param_list_path):
                return Response({'status': 'Bad Request',
                                 'message': 'Is missing files to the Round take place!'},
                                status=status.HTTP_400_BAD_REQUEST)
            try:
                with transaction.atomic():
                    s = Trial.objects.create(round=r)
            except IntegrityError:
                return Response({'status': 'Bad request',
                                 'message': 'The trial can not be created!'},
                                status=status.HTTP_400_BAD_REQUEST)

            serializer = TrialSerializer(TrialSimplex(s))
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the trial information
        B{URL:} ../api/v1/competitions/trial/<identifier>/

        :type  identifier: str
        :param identifier: The trial identifier
        """
        trial = get_object_or_404(Trial.objects.all(), identifier=kwargs.get('pk'))

        if trial.round.parent_competition.type_of_competition.name == settings.PRIVATE_COMPETITIONS_NAME:
            return Response({'status': 'Bad Request',
                             'message': 'This grid can\'t be seen!'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(TrialSimplex(trial))

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} the trial information
        B{URL:} ../api/v1/competitions/trial/<identifier>/

        :type  identifier: str
        :param identifier: The trial identifier
        """
        trial = get_object_or_404(Trial.objects.all(), identifier=kwargs.get('pk'))

        if trial.round.parent_competition.type_of_competition.name == settings.PRIVATE_COMPETITIONS_NAME:
            return Response({'status': 'Bad Request',
                             'message': 'This grid can\'t be seen!'},
                            status=status.HTTP_400_BAD_REQUEST)

        trial.delete()

        return Response({'status': 'Deleted',
                         'message': 'The trial has been deleted'},
                        status=status.HTTP_200_OK)


class GetTrialAgents(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Trial.objects.all()
    serializer_class = TrialAgentSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the trial competition agents
        B{URL:} ../api/v1/competitions/trial_agents/<identifier>/

        :type  identifier: str
        :param identifier: The trial identifier
        """
        trial = get_object_or_404(Trial.objects.all(), identifier=kwargs.get('pk'))
        trials = []

        for lga in trial.logtrialagent_set.all():
            trials += [TrialAgentSimplex(lga)]

        # Competition Agents name
        serializer = self.serializer_class(trials, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class TrialByAgent(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Trial.objects.all()
    serializer_class = TrialSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the agent trials
        B{URL:} ../api/v1/competitions/trials_by_agent/<agent_name>/?team_name=<team_name>

        :type  agent_name: str
        :param agent_name: The agent name
        :type  team_name: str
        :param team_name: The team name
        """
        if 'team_name' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?team_name=<team_name>'},
                            status=status.HTTP_400_BAD_REQUEST)

        team = get_object_or_404(Team.objects.all(), name=request.GET.get('team_name', ''))
        agent = get_object_or_404(Agent.objects.all(), team=team, agent_name=kwargs.get('pk'))
        trials = []

        for lga in LogTrialAgent.objects.filter(competition_agent=agent.competitionagent_set.all()):
            trials += [TrialSimplex(lga.trial)]

        serializer = self.serializer_class(trials, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class TrialByRound(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Trial.objects.all()
    serializer_class = TrialSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the round trials
        B{URL:} ../api/v1/competitions/trials_by_round/<round_name>/?competition_name=<competition_name>

        :type  round_name: str
        :param round_name: The round name
        :type  competition_name: str
        :param competition_name: The competition name
        """
        competition = get_object_or_404(Competition.objects.all(), name=request.GET.get('competition_name', ''))

        if competition.type_of_competition.name == settings.PRIVATE_COMPETITIONS_NAME:
            return Response({'status': 'Bad Request',
                             'message': 'This grid can\'t be seen!'},
                            status=status.HTTP_400_BAD_REQUEST)

        r = get_object_or_404(Round.objects.all(), name=kwargs.get('pk'), parent_competition=competition)
        serializer = self.serializer_class([TrialSimplex(sim) for sim in r.trial_set.all()], many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class TrialByCompetition(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Trial.objects.all()
    serializer_class = TrialSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the competition trials
        B{URL:} ../api/v1/competitions/trials_by_competition/<competition_name>/

        :type  competition_name: str
        :param competition_name: The competition name
        """
        competition = get_object_or_404(Competition.objects.all(), name=kwargs.get('pk'))

        if competition.type_of_competition.name == settings.PRIVATE_COMPETITIONS_NAME:
            return Response({'status': 'Bad Request',
                             'message': 'This grid can\'t be seen!'},
                            status=status.HTTP_400_BAD_REQUEST)

        trials = []

        for r in competition.round_set.all():
            trials += [TrialSimplex(sim) for sim in r.trial_set.all()]

        serializer = self.serializer_class(trials, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class TrialGridViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                       mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = TrialGrid.objects.all()
    serializer_class = TrialGridInputSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(), IsStaff(),

    def create(self, request, *args, **kwargs):
        """
        B{Associate} one grid to the trial
        B{URL:} ../api/v1/competitions/trial_grid/

        :type  grid_identifier: str
        :param grid_identifier: The grid identifier
        :type  trial_identifier: str
        :type  trial_identifier: The agent name
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            grid_positions = get_object_or_404(GridPositions.objects.all(),
                                               identifier=serializer.validated_data['grid_identifier'])
            trial = get_object_or_404(Trial.objects.all(),
                                      identifier=serializer.validated_data['trial_identifier'])

            teams_in_grid = len(TrialGrid.objects.filter(trial=trial))

            if teams_in_grid >= grid_positions.competition.type_of_competition.number_teams_for_trial:
                return Response({'status': 'Bad Request',
                                 'message': 'You can not add more teams to the grid.'},
                                status=status.HTTP_400_BAD_REQUEST)

            if grid_positions.competition.state_of_competition == 'Past':
                return Response({'status': 'Bad Request',
                                 'message': 'The competition is in \'Past\' state.'},
                                status=status.HTTP_400_BAD_REQUEST)

            team_enrolled = TeamEnrolled.objects.filter(team=grid_positions.team,
                                                        competition=grid_positions.competition)

            if len(team_enrolled) != 1:
                return Response({'status': 'Permission denied',
                                 'message': 'The team must be enrolled in the competition.'},
                                status=status.HTTP_403_FORBIDDEN)

            if not team_enrolled[0].valid:
                return Response({'status': 'Permission denied',
                                 'message': 'The team must be enrolled in the competition with valid inscription.'},
                                status=status.HTTP_403_FORBIDDEN)

            if serializer.validated_data['position'] > \
                    grid_positions.competition.type_of_competition.number_teams_for_trial:
                return Response({'status': 'Permission denied',
                                 'message': 'The position can\'t be higher than the number of teams allowed by trial.'},
                                status=status.HTTP_403_FORBIDDEN)

            if len(TrialGrid.objects.filter(trial=trial,
                                            position=serializer.validated_data['position'])) != 0:
                return Response({'status': 'Bad Request',
                                 'message': 'The position has already been taken.'},
                                status=status.HTTP_403_FORBIDDEN)
            try:
                with transaction.atomic():
                    TrialGrid.objects.create(grid_positions=grid_positions, trial=trial,
                                             position=serializer.validated_data['position'])
            except IntegrityError:
                return Response({'status': 'Bad request',
                                 'message': 'The team can\'t be associated!'},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} grid positions by trial
        B{URL:} ../api/v1/competitions/trial_grid/<trial_identifier>/

        :type  trial_identifier: str
        :param trial_identifier: The trial identifier
        """
        trial = get_object_or_404(Trial.objects.all(), identifier=kwargs.get('pk', ''))
        grid_sim_list = TrialGrid.objects.filter(trial=trial)

        serializer = TrialGridsSerializer([TrialGridSimplex(gs) for gs in grid_sim_list], many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        B{Dissociate} one grid to the trial
        B{URL:} ../api/v1/competitions/trial_grid/trial_identifier/?position=<position>

        :type  position: str
        :param position: The position
        :type  trial_identifier: str
        :type  trial_identifier: The agent name
        """
        sim = get_object_or_404(Trial.objects.all(), identifier=kwargs.get('pk', ''))
        sim_grid = get_object_or_404(TrialGrid.objects.all(), trial=sim,
                                     position=request.GET.get('position', ''))

        if sim_grid.grid_positions.competition.state_of_competition == 'Past':
            return Response({'status': 'Bad Request',
                             'message': 'The competition is in \'Past\' state.'},
                            status=status.HTTP_400_BAD_REQUEST)

        team_enrolled = TeamEnrolled.objects.filter(team=sim_grid.grid_positions.team,
                                                    competition=sim_grid.grid_positions.competition)

        if len(team_enrolled) != 1:
            return Response({'status': 'Permission denied',
                             'message': 'The team must be enrolled in the competition.'},
                            status=status.HTTP_403_FORBIDDEN)

        if not team_enrolled[0].valid:
            return Response({'status': 'Permission denied',
                             'message': 'The team must be enrolled in the competition with valid inscription.'},
                            status=status.HTTP_403_FORBIDDEN)

        sim = get_object_or_404(TrialGrid.objects.all(), trial=sim, position=request.GET.get('position', ''))
        sim.delete()

        return Response({'status': 'Deleted',
                         'message': 'The grid has been dissociated!'},
                        status=status.HTTP_200_OK)


class PrepareTrial(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Trial.objects.all()
    serializer_class = TrialSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(), IsStaff(),

    def create(self, request, *args, **kwargs):
        """
        B{Prepare} the trial
        B{URL:} ../api/v1/trials/prepare/

        :type  trial_id: str
        :param trial_id: The trial id
        """
        trial = get_object_or_404(Trial.objects.all(), identifier=request.data.get('trial_id', ''))

        if not trial_not_started(trial):
            return Response({'status': 'Bad Request',
                             'message': 'The trial must be in state READY!'},
                            status=status.HTTP_400_BAD_REQUEST)

        trial_grids = TrialGrid.objects.filter(trial=trial)

        # verify if round has files
        if not bool(trial.round.grid_path) or not bool(trial.round.param_list_path) \
                or not bool(trial.round.param_list_path):
            return Response({'status': 'Bad Request',
                             'message': 'Is missing files to the Round take place!'},
                            status=status.HTTP_400_BAD_REQUEST)

        if len(trial_grids) == 0:
            return Response({'status': 'Bad Request',
                             'message': 'Please select teams to go to the Trial!'},
                            status=status.HTTP_400_BAD_REQUEST)

        pos = 1

        for trial_grid in trial_grids:
            grid_positions = trial_grid.grid_positions
            agents_grid = AgentGrid.objects.filter(grid_position=grid_positions)

            for agent_grid in agents_grid:
                # print agent_grid.position

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
                         'message': 'The trial is now in \"Prepare\" state!'},
                        status=status.HTTP_200_OK)


class StartTrial(views.APIView):
    def get_permissions(self):
        return permissions.IsAuthenticated(), IsStaff(),

    @staticmethod
    def post(request):
        """
        B{Start} the trial
        B{URL:} ../api/v1/trials/start/

        :type  trial_id: str
        :param trial_id: The trial id
        """
        trial = get_object_or_404(Trial.objects.all(), identifier=request.data.get('trial_id', ''))

        # verify if the round doesn't started already
        if not trial_prepare(trial):
            return Response({'status': 'Bad Request',
                             'message': 'The trial must be in state PREPARE!'},
                            status=status.HTTP_400_BAD_REQUEST)

        # verify if round has files
        if not bool(trial.round.grid_path) or not bool(trial.round.param_list_path) \
                or not bool(trial.round.param_list_path):
            return Response({'status': 'Bad Request',
                             'message': 'Is missing files to the Round take place!'},
                            status=status.HTTP_400_BAD_REQUEST)

        trial_grids = TrialGrid.objects.filter(trial=trial)

        if len(trial_grids) == 0:
            return Response({'status': 'Bad Request',
                             'message': 'Please select teams to go to the Trial!'},
                            status=status.HTTP_400_BAD_REQUEST)

        params = {'trial_identifier': trial.identifier}

        try:
            requests.post(settings.START_SIM_ENDPOINT, params)
        except requests.ConnectionError:
            return Response({'status': 'Bad Request',
                             'message': 'The simulator appears to be down!'},
                            status=status.HTTP_400_BAD_REQUEST)

        # sim now goes to "started"
        trial.waiting = False
        trial.prepare = False
        trial.started = True
        trial.save()

        NotificationBroadcast.add(channel="user", status="ok",
                                  message="The trial of " + trial.round.name + " has started!",
                                  trigger="trial_start")

        return Response({'status': 'Trial started',
                         'message': 'Please wait that the trial starts at the simulator!'},
                        status=status.HTTP_200_OK)
