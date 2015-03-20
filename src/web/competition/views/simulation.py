from django.shortcuts import get_object_or_404
from competition.models import Competition, Round, Simulation, CompetitionAgent, Agent, \
    LogSimulationAgent
from competition.serializers import SimulationXSerializer, \
    SimulationSerializer, \
    SimulationAgentSerializer, LogSimulation
import os
from rest_framework import permissions
from rest_framework import mixins, viewsets, status, views
from rest_framework.response import Response
from competition.permissions import IsAdmin
from django.conf import settings
from competition.shortcuts import *
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from competition.views.simplex import SimulationSimplex, SimulationAgentSimplex, SimulationX
import requests


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
        B{Create} one simulation for one round
        B{URL:} ../api/v1/competitions/simulation/

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
        B{Get} the simulation information
        B{URL:} ../api/v1/competitions/simulation/<identifier>/

        @type  identifier: str
        @param identifier: The simulation identifier
        """
        simulation = get_object_or_404(Simulation.objects.all(), identifier=kwargs.get('pk'))
        serializer = self.serializer_class(SimulationSimplex(simulation))

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} the simulation information
        B{URL:} ../api/v1/competitions/simulation/<identifier>/

        @type  identifier: str
        @param identifier: The simulation identifier
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
        B{Get} the simulation competition agents
        B{URL:} ../api/v1/competitions/simulation_agents/<identifier>/

        @type  identifier: str
        @param identifier: The simulation identifier
        """
        simulation = get_object_or_404(Simulation.objects.all(), identifier=kwargs.get('pk'))

        simulations = []
        lgas = LogSimulationAgent.objects.filter(simulation=simulation)

        for lga in lgas:
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
        B{Associate} one agent to one simulation
        B{URL:} ../api/v1/competitions/associate_agent_to_simulation/

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

            simulation = get_object_or_404(Simulation.objects.all(),
                identifier=serializer.validated_data['simulation_identifier'])

            maxs = dict(settings.NUMBER_AGENTS_BY_SIMULATION)

            # competitiva
            if competition_agent.competition.type_of_competition == settings.COLABORATIVA:
                # see if the simulation has already the number max of agents
                simulation_agents = LogSimulationAgent.objects.filter(simulation=simulation)
                if len(simulation_agents) >= maxs[settings.COLABORATIVA]:
                    return Response({'status': 'Bad Request',
                                     'message': 'The simulation reached the number max of participants.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                # all the agents must be part of the same team
                group = agent.group
                for simulation_agent in simulation_agents:
                    if simulation_agent.competition_agent.agent.group != group:
                        return Response({'status': 'Bad Request',
                                         'message': 'The competition is in ' + settings.COLABORATIVA + ' mode, the agents must be owned by the same team.'},
                                        status=status.HTTP_400_BAD_REQUEST)

            # colaborativa
            if competition_agent.competition.type_of_competition == settings.COMPETITIVA:
                # see if the simulation has already the number max of agents
                simulation_agents = LogSimulationAgent.objects.filter(simulation=simulation)
                if len(simulation_agents) >= maxs[settings.COMPETITIVA]:
                    return Response({'status': 'Bad Request',
                                     'message': 'The simulation reached the number max of participants.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                # all the agents must be from different teams
                group = agent.group
                for simulation_agent in simulation_agents:
                    if simulation_agent.competition_agent.agent.group == group:
                        return Response({'status': 'Bad Request',
                                         'message': 'The competition is in ' + settings.COLABORATIVA + ' mode, the agents must be from different teams.'},
                                        status=status.HTTP_400_BAD_REQUEST)

            # Reload values
            r = get_object_or_404(Round.objects.all(), name=serializer.validated_data['round_name'])
            agent = get_object_or_404(Agent.objects.all(), agent_name=serializer.validated_data['agent_name'])
            competition_agent = get_object_or_404(CompetitionAgent.objects.all(), round=r, agent=agent)
            simulation = get_object_or_404(Simulation.objects.all(),
                identifier=serializer.validated_data['simulation_identifier'])

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
        B{Destroy} one agent to one simulation
        B{URL:} ../api/v1/competitions/associate_agent_to_simulation/<simulation_identifier>/

        @type  round_name: str
        @param round_name: The round name
        @type  agent_name: str
        @param agent_name: The agent name
        @type  pos: int
        @param pos: The agent position
        """
        simulation = get_object_or_404(Simulation.objects.all(), identifier=kwargs.get('pk'))
        r = get_object_or_404(Round.objects.all(), name=request.data.get('round_name', ''))
        agent = get_object_or_404(Agent.objects.all(), agent_name=request.data.get('agent_name', ''))
        competition_agent = get_object_or_404(CompetitionAgent.objects.all(), round=r, agent=agent)
        lsa = get_object_or_404(LogSimulationAgent.objects.all(), competition_agent=competition_agent,
            simulation=simulation, pos=request.data.get('pos', ''))
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
        B{Get} the agent simulations
        B{URL:} ../api/v1/competitions/simulations_by_agent/<agent_name>/

        @type  agent_name: str
        @param agent_name: The agent name
        """
        agent = get_object_or_404(Agent.objects.all(), agent_name=kwargs.get('pk'))
        competition_agents = CompetitionAgent.objects.filter(agent=agent)
        simulations = []

        for competition_agent in competition_agents:
            lgas = LogSimulationAgent.objects.filter(competition_agent=competition_agent)
            for lga in lgas:
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
        B{Get} the round simulations
        B{URL:} ../api/v1/competitions/simulations_by_round/<round_name>/

        @type  round_name: str
        @param round_name: The round name
        """
        r = get_object_or_404(Round.objects.all(), name=kwargs.get('pk'))
        competition_agents = CompetitionAgent.objects.filter(round=r)
        simulations = []

        for competition_agent in competition_agents:
            lgas = LogSimulationAgent.objects.filter(competition_agent=competition_agent)
            for lga in lgas:
                simulations += [SimulationSimplex(lga.simulation)]

        serializer = self.serializer_class(simulations, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SaveLogs(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Simulation.objects.all()
    serializer_class = LogSimulation

    """
    Must be discussed one simple way of authentication server to server
    """

    def create(self, request, *args, **kwargs):
        """
        B{Create} the json log
        B{URL:} ../api/v1/competitions/simulation_log/

        @type  log_json: str
        @param log_json: The json log
        @type  simulation_identifier: str
        @param simulation_identifier: The simulation identifier
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            simulation = Simulation.objects.get(identifier=serializer.validated_data['simulation_identifier'])

            if not simulation_started(simulation):
                return Response({'status': 'Bad Request',
                                 'message': 'The simulation should be stated first!'},
                                status=status.HTTP_400_BAD_REQUEST)

            simulation.log_json = serializer.validated_data['log_json']
            simulation.save()
            return Response({'status': 'Created',
                             'message': 'The log has been uploaded!'}, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': 'The simulation couldn\'t be updated with that data.'},
                        status=status.HTTP_400_BAD_REQUEST)


class GetSimulationLog(views.APIView):
    @staticmethod
    def get(request, simulation_id):
        """
        B{Get} simulation json log
        B{URL:} ../api/v1/competitions/get_simulation_log/<simulation_id>/

        @type  simulation_id: str
        @param simulation_id: The simulation identifier
        """
        simulation = get_object_or_404(Simulation.objects.all(), identifier=simulation_id)

        if not simulation_done(simulation):
            return Response({'status': 'Bad request',
                             'message': 'The simulation must have a log!'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            file = default_storage.open(simulation.log_json)
        except Exception:
            return Response({'status': 'Bad request',
                             'message': 'The file doesn\'t exists'},
                            status=status.HTTP_400_BAD_REQUEST)

        wrapper = FileWrapper(file)
        response = HttpResponse(wrapper, content_type="application/x-compressed")
        response['Content-Disposition'] = 'attachment; filename=' + simulation_id + '.tar.gz'
        response['Content-Length'] = os.path.getsize(file.name)
        file.seek(0)
        return response


class SimulationByCompetition(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Simulation.objects.all()
    serializer_class = SimulationSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the competition simulations
        B{URL:} ../api/v1/competitions/simulations_by_competition/<competition_name>/

        @type  competition_name: str
        @param competition_name: The competition name
        """
        competition = get_object_or_404(Competition.objects.all(), name=kwargs.get('pk'))
        competition_agents = CompetitionAgent.objects.filter(competition=competition)
        simulations = []

        for competition_agent in competition_agents:
            lgas = LogSimulationAgent.objects.filter(competition_agent=competition_agent)
            for lga in lgas:
                simulations += [SimulationSimplex(lga.simulation)]

        serializer = self.serializer_class(simulations, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class StartSimulation(views.APIView):
    def get_permissions(self):
        return permissions.IsAuthenticated(), IsAdmin(),

    @staticmethod
    def post(request):
        """
        B{Start} the simulation
        B{URL:} ../api/v1/competitions/start_simulation/

        @type  simulation_id: str
        @param simulation_id: The simulation id
        """
        simulation = get_object_or_404(Simulation.objects.all(), identifier=request.data.get('simulation_id', ''))
        if simulation_waiting(simulation):
            params = {'simulation_identifier': "0a256950-7a5c-403d-aba3-52e455d197c5"}

            try:
                result = requests.post(settings.START_SIM_ENDPOINT, params)
            except requests.ConnectionError:
                return Response({'status': 'Bad Request',
                                 'message': 'The simulator appears to be down!'},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response({'status': 'Simulation started',
                             'message': 'Please wait that the simulation starts at the simulator!'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'status': 'Bad Request',
                             'message': 'The simulation must be in state: waiting!'},
                            status=status.HTTP_400_BAD_REQUEST)


class GetSimulation(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Simulation.objects.all()
    serializer_class = SimulationXSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the simulation complete, machine-to-machine
        B{URL:} ../api/v1/competitions/get_simulation/<simulation_id>/

        @type  simulation_id: str
        @param simulation_id: The simulation id
        """
        simulation = get_object_or_404(self.queryset, identifier=kwargs.get('pk'))
        serializer = self.serializer_class(SimulationX(simulation))
        simulation.started = True
        simulation.save()

        return Response(serializer.data, status=status.HTTP_200_OK)