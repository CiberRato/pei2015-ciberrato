from django.shortcuts import get_object_or_404, get_list_or_404
from django.conf import settings

import requests

from rest_framework import permissions
from rest_framework import mixins, viewsets, status, views
from rest_framework.response import Response

from agent.models import Agent

from .simplex import SimulationSimplex, SimulationAgentSimplex, SimulationGridSimplex
from ..serializers import SimulationSerializer, SimulationAgentSerializer, SimulationGridsSerializer, \
    SimulationGridInputSerializer
from ..models import Competition, Round, Simulation, CompetitionAgent, LogSimulationAgent, SimulationGrid, \
    GridPositions, GroupEnrolled, AgentGrid
from ..shortcuts import *
from ..permissions import IsStaff


class SimulationViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                        mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Simulation.objects.all()
    serializer_class = SimulationSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),
        return permissions.IsAuthenticated(), IsStaff(),

    def create(self, request, *args, **kwargs):
        """
        B{Create} one trial for one round
        B{URL:} ../api/v1/competitions/trial/

        @type  round_name: str
        @param round_name: The round name
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            r = get_object_or_404(Round.objects.all(), name=serializer.validated_data['round_name'])
            s = Simulation.objects.create(round=r)
            serializer = SimulationSerializer(SimulationSimplex(s))
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the trial information
        B{URL:} ../api/v1/competitions/trial/<identifier>/

        @type  identifier: str
        @param identifier: The trial identifier
        """
        simulation = get_object_or_404(Simulation.objects.all(), identifier=kwargs.get('pk'))
        serializer = self.serializer_class(SimulationSimplex(simulation))

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} the trial information
        B{URL:} ../api/v1/competitions/trial/<identifier>/

        @type  identifier: str
        @param identifier: The trial identifier
        """
        simulation = get_object_or_404(Simulation.objects.all(), identifier=kwargs.get('pk'))
        simulation.delete()

        return Response({'status': 'Deleted',
                         'message': 'The simulation has been deleted'},
                        status=status.HTTP_200_OK)


class GetSimulationAgents(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Simulation.objects.all()
    serializer_class = SimulationAgentSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the trial competition agents
        B{URL:} ../api/v1/competitions/trial_agents/<identifier>/

        @type  identifier: str
        @param identifier: The trial identifier
        """
        simulation = get_object_or_404(Simulation.objects.all(), identifier=kwargs.get('pk'))
        simulations = []

        for lga in simulation.logsimulationagent_set.all():
            simulations += [SimulationAgentSimplex(lga)]

        # Competition Agents name
        serializer = self.serializer_class(simulations, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SimulationByAgent(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Simulation.objects.all()
    serializer_class = SimulationSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the agent trials
        B{URL:} ../api/v1/competitions/trials_by_agent/<agent_name>/

        @type  agent_name: str
        @param agent_name: The agent name
        """
        agent = get_object_or_404(Agent.objects.all(), agent_name=kwargs.get('pk'))
        simulations = []

        for competition_agent in agent.competitionagent_set.all():
            for lga in LogSimulationAgent.objects.filter(competition_agent=competition_agent):
                simulations += [SimulationSimplex(lga.simulation)]

        serializer = self.serializer_class(simulations, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SimulationByRound(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Simulation.objects.all()
    serializer_class = SimulationSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the round trials
        B{URL:} ../api/v1/competitions/trials_by_round/<round_name>/

        @type  round_name: str
        @param round_name: The round name
        """
        r = get_object_or_404(Round.objects.all(), name=kwargs.get('pk'))
        serializer = self.serializer_class([SimulationSimplex(sim) for sim in r.simulation_set.all()], many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SimulationByCompetition(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Simulation.objects.all()
    serializer_class = SimulationSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the competition trials
        B{URL:} ../api/v1/competitions/trials_by_competition/<competition_name>/

        @type  competition_name: str
        @param competition_name: The competition name
        """
        competition = get_object_or_404(Competition.objects.all(), name=kwargs.get('pk'))
        simulations = []

        for r in competition.round_set.all():
            simulations += [SimulationSimplex(sim) for sim in r.simulation_set.all()]

        serializer = self.serializer_class(simulations, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SimulationGridViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                            mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = SimulationGrid.objects.all()
    serializer_class = SimulationGridInputSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(), IsStaff(),

    def create(self, request, *args, **kwargs):
        """
        B{Associate} one grid to the simulation
        B{URL:} ../api/v1/competitions/simulation_grid/

        @type  grid_identifier: str
        @param grid_identifier: The grid identifier
        @type  simulation_identifier: str
        @type  simulation_identifier: The agent name
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            grid_positions = get_object_or_404(GridPositions.objects.all(),
                identifier=serializer.validated_data['grid_identifier'])
            simulation = get_object_or_404(Simulation.objects.all(),
                identifier=serializer.validated_data['simulation_identifier'])

            groups_in_grid = len(SimulationGrid.objects.filter(simulation=simulation))

            if groups_in_grid >= grid_positions.competition.type_of_competition.number_teams_for_trial:
                return Response({'status': 'Bad Request',
                                 'message': 'You can not add more groups to the grid.'},
                                status=status.HTTP_400_BAD_REQUEST)

            if grid_positions.competition.state_of_competition == 'Past':
                return Response({'status': 'Bad Request',
                                 'message': 'The competition is in \'Past\' state.'},
                                status=status.HTTP_400_BAD_REQUEST)

            group_enrolled = GroupEnrolled.objects.filter(group=grid_positions.group,
                                                          competition=grid_positions.competition)

            if len(group_enrolled) != 1:
                return Response({'status': 'Permission denied',
                                 'message': 'The group must be enrolled in the competition.'},
                                status=status.HTTP_403_FORBIDDEN)

            if not group_enrolled[0].valid:
                return Response({'status': 'Permission denied',
                                 'message': 'The group must be enrolled in the competition with valid inscription.'},
                                status=status.HTTP_403_FORBIDDEN)

            if serializer.validated_data[
                'position'] > grid_positions.competition.type_of_competition.number_teams_for_trial:
                return Response({'status': 'Permission denied',
                                 'message': 'The position can\'t be higher than the number of teams allowed by trial.'},
                                status=status.HTTP_403_FORBIDDEN)

            if len(SimulationGrid.objects.filter(grid_positions=grid_positions,
                                                 position=serializer.validated_data['position'])) != 0:
                return Response({'status': 'Permission denied',
                                 'message': 'The position has already been taken.'},
                                status=status.HTTP_403_FORBIDDEN)

            SimulationGrid.objects.create(grid_positions=grid_positions, simulation=simulation,
                                          position=serializer.validated_data['position'])

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} grid positions by simulation
        B{URL:} ../api/v1/competitions/simulation_grid/<simulation_identifier>/

        @type  simulation_identifier: str
        @param simulation_identifier: The simulation identifier
        """
        simulation = get_object_or_404(Simulation.objects.all(), identifier=kwargs.get('pk', ''))
        grid_sim_list = SimulationGrid.objects.filter(simulation=simulation)

        serializer = SimulationGridsSerializer([SimulationGridSimplex(gs) for gs in grid_sim_list], many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        B{Dissociate} one grid to the simulation
        B{URL:} ../api/v1/competitions/simulation_grid/simulation_identifier/?position=<position>

        @type  position: str
        @param position: The position
        @type  simulation_identifier: str
        @type  simulation_identifier: The agent name
        """
        sim = get_object_or_404(Simulation.objects.all(), identifier=kwargs.get('pk', ''))
        sim_grid = get_object_or_404(SimulationGrid.objects.all(), simulation=sim,
            position=request.GET.get('position', ''))

        if sim_grid.grid_positions.competition.state_of_competition == 'Past':
            return Response({'status': 'Bad Request',
                             'message': 'The competition is in \'Past\' state.'},
                            status=status.HTTP_400_BAD_REQUEST)

        group_enrolled = GroupEnrolled.objects.filter(group=sim_grid.grid_positions.group,
                                                      competition=sim_grid.grid_positions.competition)

        if len(group_enrolled) != 1:
            return Response({'status': 'Permission denied',
                             'message': 'The group must be enrolled in the competition.'},
                            status=status.HTTP_403_FORBIDDEN)

        if not group_enrolled[0].valid:
            return Response({'status': 'Permission denied',
                             'message': 'The group must be enrolled in the competition with valid inscription.'},
                            status=status.HTTP_403_FORBIDDEN)

        sim = get_object_or_404(SimulationGrid.objects.all(), simulation=sim, position=request.GET.get('position', ''))
        sim.delete()

        return Response({'status': 'Deleted',
                         'message': 'The grid has been dissociated!'},
                        status=status.HTTP_200_OK)


class StartSimulation(views.APIView):
    def get_permissions(self):
        return permissions.IsAuthenticated(), IsStaff(),

    @staticmethod
    def post(request):
        """
        B{Start} the simulation
        B{URL:} ../api/v1/competitions/start_trial/

        @type  trial_id: str
        @param trial_id: The trial id
        """
        simulation = get_object_or_404(Simulation.objects.all(), identifier=request.data.get('trial_id', ''))
        simulation_grids = SimulationGrid.objects.filter(simulation=simulation)

        pos = 1

        for simulation_grid in simulation_grids:
            grid_positions = simulation_grid.grid_positions
            agents_grid = AgentGrid.objects.filter(grid_position=grid_positions)

            # print simulation_grid.position

            for agent_grid in agents_grid:
                # print agent_grid.position

                if agent_grid.agent.code_valid:
                    group_enroll = GroupEnrolled.objects.get(group=agent_grid.agent.group,
                                                             competition=simulation.round.parent_competition)
                    if group_enroll.valid:
                        # competition agent
                        competition_agent_not_exists = (len(CompetitionAgent.objects.filter(
                            competition=simulation.round.parent_competition,
                            agent=agent_grid.agent,
                            round=simulation.round)) == 0)

                        if competition_agent_not_exists:
                            competition_agent = CompetitionAgent.objects.create(
                                competition=simulation.round.parent_competition,
                                agent=agent_grid.agent,
                                round=simulation.round)
                        else:
                            competition_agent = CompetitionAgent.objects.get(
                                competition=simulation.round.parent_competition,
                                agent=agent_grid.agent,
                                round=simulation.round)

                        # log simulation agent
                        LogSimulationAgent.objects.create(competition_agent=competition_agent, simulation=simulation,
                                                          pos=pos)
                        pos += 1

        if simulation_waiting(simulation):
            params = {'trial_id': simulation.identifier}

            try:
                requests.post(settings.START_SIM_ENDPOINT, params)
            except requests.ConnectionError:
                return Response({'status': 'Bad Request',
                                 'message': 'The simulator appears to be down!'},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response({'status': 'Trial started',
                             'message': 'Please wait that the trial starts at the simulator!'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'status': 'Bad Request',
                             'message': 'The trial must be in state: waiting!'},
                            status=status.HTTP_400_BAD_REQUEST)