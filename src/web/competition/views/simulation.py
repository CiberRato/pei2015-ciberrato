from django.shortcuts import get_object_or_404
from competition.models import Competition, Round, Simulation, CompetitionAgent, Agent, \
    LogSimulationAgent
from competition.serializers import SimulationXSerializer, \
    SimulationSerializer, \
    SimulationAgentSerializer, LogSimulation
from rest_framework import permissions
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from competition.permissions import IsAdmin
from django.conf import settings
from competition.views.simplex import SimulationSimplex, SimulationAgentSimplex


class SimulationViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                        mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Simulation.objects.all()
    serializer_class = SimulationSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),
        return permissions.IsAuthenticated(), IsAdmin(),

    def create(self, request, *args, **kwargs):
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


class AssociateAgentToSimulation(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = LogSimulationAgent.objects.all()
    serializer_class = SimulationAgentSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            r = get_object_or_404(Round.objects.all(), name=serializer.validated_data['round_name'])
            agent = get_object_or_404(Agent.objects.all(), agent_name=serializer.validated_data['agent_name'])

            competition_agent = get_object_or_404(CompetitionAgent.objects.all(), round=r, agent=agent)

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
                                         'message': 'The competition is in Colaborativa mode, the agents must be owned by the same team.'},
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
                                         'message': 'The competition is in Colaborativa mode, the agents must be from different teams.'},
                                        status=status.HTTP_400_BAD_REQUEST)

            lsa = LogSimulationAgent.objects.create(competition_agent=competition_agent, simulation=simulation,
                                                    pos=serializer.validated_data['pos'])
            serializer = SimulationAgentSerializer(SimulationAgentSimplex(lsa))

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': 'The simulation agent could not be created with received data'},
                        status=status.HTTP_400_BAD_REQUEST)


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


class SaveLogs(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Simulation.objects.all()
    serializer_class = LogSimulation

    def create(self, request, *args, **kwargs):
        """
        B{Create} the xml and json log
        B{URL:} ../api/v1/competitions/simulation_log/

        @type  log_json: str
        @param log_json: The json log
        @type  simulation_log_xml: str
        @param simulation_log_xml: The xml log
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            simulation = Simulation.objects.get(identifier=serializer.validated_data['simulation_identifier'])
            simulation.log_json = serializer.validated_data['log_json']
            simulation.simulation_log_xml = serializer.validated_data['simulation_log_xml']
            simulation.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'status': 'Bad Request',
                         'message': 'The simulation couldn\'t be updated with that data.'},
                        status=status.HTTP_400_BAD_REQUEST)


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


class GetSimulations(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Simulation.objects.all()
    serializer_class = SimulationXSerializer

    def list(self, request, *args, **kwargs):
        class AgentX():
            def __init__(self, log_simulation_agent, simulation_id):
                if log_simulation_agent.competition_agent.agent.is_virtual:
                    self.agent_type = "virtual"
                else:
                    self.agent_type = "local"

                self.agent_name = log_simulation_agent.competition_agent.agent.agent_name
                self.pos = log_simulation_agent.pos
                self.language = log_simulation_agent.competition_agent.agent.language

                if not log_simulation_agent.competition_agent.agent.is_virtual:
                    # o agent tem de estar na simulacao
                    # autenticacao para receber estes dados
                    self.files = "/api/v1/competitions/agent_file/" + simulation_id + "/" + log_simulation_agent.competition_agent.agent.agent_name + "/"

        class SimulationX():
            def __init__(self, simulation):
                self.simulation_id = simulation.identifier
                # a competicao nao pode estar em register
                self.grid = "/api/v1/competitions/round_file/" + simulation.round.name + "/?file=grid"
                self.param_list = "/api/v1/competitions/round_file/" + simulation.round.name + "/?file=param_list"
                self.lab = "/api/v1/competitions/round_file/" + simulation.round.name + "/?file=lab"

                # get the agents
                log_simulation_agents = LogSimulationAgent.objects.filter(simulation=simulation)
                self.agents = []
                for log_simulation_agent in log_simulation_agents:
                    self.agents += [AgentX(log_simulation_agent, self.simulation_id)]

        simulations = [SimulationX(simulation) for simulation in Simulation.objects.all()]

        serializer = self.serializer_class(simulations, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
