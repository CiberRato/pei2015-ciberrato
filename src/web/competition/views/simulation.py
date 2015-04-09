from django.shortcuts import get_object_or_404
from django.conf import settings

import requests

from rest_framework import permissions
from rest_framework import mixins, viewsets, status, views
from rest_framework.response import Response

from agent.models import Agent

from .simplex import SimulationSimplex, SimulationAgentSimplex
from ..serializers import SimulationSerializer, SimulationAgentSerializer
from ..models import Competition, Round, Simulation, CompetitionAgent, LogSimulationAgent
from ..shortcuts import *
from ..permissions import IsAdmin


class SimulationViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                        mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Simulation.objects.all()
    serializer_class = SimulationSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),
        return permissions.IsAuthenticated(), IsAdmin(),

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
                         'message': 'The simulation could not be created with received data'},
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

        cp = CompetitionAgent.objects.filter(round=simulation.round)

        for agent in cp:
            agent.eligible = True
            agent.save()

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


class AssociateAgentToSimulation(mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = LogSimulationAgent.objects.all()
    serializer_class = SimulationAgentSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(), IsAdmin(),

    def create(self, request, *args, **kwargs):
        """
        B{Associate} one agent to one trial
        B{URL:} ../api/v1/competitions/associate_agent_to_trial/

        @type  round_name: str
        @param round_name: The round name
        @type  simulation_identifier: str
        @param simulation_identifier: The simulation identifier
        @type  agent_name: str
        @param agent_name: The agent name
        @type  pos: int
        @param pos: The agent position
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            r = get_object_or_404(Round.objects.all(), name=serializer.validated_data['round_name'])
            agent = get_object_or_404(Agent.objects.all(), agent_name=serializer.validated_data['agent_name'])

            competition_agent = get_object_or_404(CompetitionAgent.objects.all(), round=r, agent=agent)

            # see if the agent is no more eligible
            if not competition_agent.eligible:
                return Response({'status': 'Bad Request',
                                 'message': 'This agent has already in one simulation!'},
                                status=status.HTTP_400_BAD_REQUEST)

            simulation = get_object_or_404(Simulation.objects.all(), identifier=serializer.validated_data['simulation_identifier'])

            """
            maxs = dict(settings.NUMBER_AGENTS_BY_SIMULATION)

            # competitiva
            if competition_agent.competition.type_of_competition == settings.COLABORATIVA:
                # see if the simulation has already the number max of agents
                if len(simulation.logsimulationagent_set.all()) >= maxs[settings.COLABORATIVA]:
                    return Response({'status': 'Bad Request',
                                     'message': 'The simulation reached the number max of participants.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                # all the agents must be part of the same team
                group = agent.group
                for simulation_agent in simulation.logsimulationagent_set.all():
                    if simulation_agent.competition_agent.agent.group != group:
                        return Response({'status': 'Bad Request',
                                         'message': 'The competition is in ' + settings.COLABORATIVA + ' mode, the agents must be owned by the same team.'},
                                        status=status.HTTP_400_BAD_REQUEST)

            # colaborativa
            if competition_agent.competition.type_of_competition == settings.COMPETITIVA:
                # see if the simulation has already the number max of agents
                if len(simulation.logsimulationagent_set.all()) >= maxs[settings.COMPETITIVA]:
                    return Response({'status': 'Bad Request',
                                     'message': 'The simulation reached the number max of participants.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                # all the agents must be from different teams
                group = agent.group
                for simulation_agent in simulation.logsimulationagent_set.all():
                    if simulation_agent.competition_agent.agent.group == group:
                        return Response({'status': 'Bad Request',
                                         'message': 'The competition is in ' + settings.COLABORATIVA + ' mode, the agents must be from different teams.'},
                                        status=status.HTTP_400_BAD_REQUEST)
            """

            # Reload values
            r = get_object_or_404(Round.objects.all(), name=serializer.validated_data['round_name'])
            agent = get_object_or_404(Agent.objects.all(), agent_name=serializer.validated_data['agent_name'])
            competition_agent = get_object_or_404(CompetitionAgent.objects.all(), round=r, agent=agent)
            simulation = get_object_or_404(Simulation.objects.all(), identifier=serializer.validated_data['simulation_identifier'])

            lsa = LogSimulationAgent.objects.create(competition_agent=competition_agent, simulation=simulation,
                                                    pos=serializer.validated_data['pos'])

            competition_agent.eligible = False
            competition_agent.save()

            serializer = SimulationAgentSerializer(SimulationAgentSimplex(lsa))

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': 'The simulation agent could not be created with received data'},
                        status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} one agent to one trial
        B{URL:} ../api/v1/competitions/associate_agent_to_trial/<trial_identifier>/

        @type  round_name: str
        @param round_name: The round name
        @type  agent_name: str
        @param agent_name: The agent name
        """
        simulation = get_object_or_404(Simulation.objects.all(), identifier=kwargs.get('pk'))
        r = get_object_or_404(Round.objects.all(), name=request.GET.get('round_name', ''))
        agent = get_object_or_404(Agent.objects.all(), agent_name=request.GET.get('agent_name', ''))
        competition_agent = get_object_or_404(CompetitionAgent.objects.all(), round=r, agent=agent)
        competition_agent.eligible = True
        competition_agent.save()
        lsa = get_object_or_404(LogSimulationAgent.objects.all(), competition_agent=competition_agent,
            simulation=simulation)
        lsa.delete()

        return Response({'status': 'Deleted',
                         'message': 'The simulation agent has been deleted!'},
                        status=status.HTTP_200_OK)


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


class StartSimulation(views.APIView):
    def get_permissions(self):
        return permissions.IsAuthenticated(), IsAdmin(),

    @staticmethod
    def post(request):
        """
        B{Start} the simulation
        B{URL:} ../api/v1/competitions/start_trial/

        @type  trial_id: str
        @param trial_id: The trial id
        """
        simulation = get_object_or_404(Simulation.objects.all(), identifier=request.data.get('trial_id', ''))
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