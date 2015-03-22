from django.shortcuts import get_object_or_404
from django.conf import settings

from rest_framework import permissions
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response

from authentication.models import Group, GroupMember

from ..models import Round, GroupEnrolled, CompetitionAgent, Competition
from ..serializers import RoundAgentSerializer, CompetitionAgentSerializer
from ..permissions import IsAdmin

from agent.simplex import AgentSimplex
from agent.serializers import AgentSerializer
from agent.models import Agent


class AssociateAgent(mixins.DestroyModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = CompetitionAgent.objects.all()
    serializer_class = CompetitionAgentSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def create(self, request, *args, **kwargs):
        """
        B{Associate} an agent
        B{URL:} ../api/v1/competitions/associate_agent/

        @type  competition_name: str
        @param competition_name: The competition name
        @type  agent_name: str
        @param agent_name: The agent name
        """

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            competition = get_object_or_404(Competition.objects.all(),
                name=serializer.validated_data['competition_name'])
            agent = get_object_or_404(Agent.objects.all(), agent_name=serializer.validated_data['agent_name'])

            if competition.state_of_competition != "Register":
                return Response({'status': 'Not allowed',
                                 'message': 'The competition is not accepting agents.'},
                                status=status.HTTP_401_UNAUTHORIZED)

            if len(GroupMember.objects.filter(group=agent.group, account=request.user)) != 1:
                return Response({'status': 'Permission denied',
                                 'message': 'You must be part of the group.'},
                                status=status.HTTP_403_FORBIDDEN)

            if len(GroupEnrolled.objects.filter(group=agent.group, competition=competition, valid=True)) != 1:
                return Response({'status': 'Permission denied',
                                 'message': 'The group must first enroll and with inscription valid.'},
                                status=status.HTTP_403_FORBIDDEN)

            # code valid
            if not agent.is_virtual and not agent.code_valid:
                return Response({'status': 'The agent code is not valid!',
                                 'message': 'Please submit a valid code first!'},
                                status=status.HTTP_400_BAD_REQUEST)


            # verify limits
            groups_agents_in_round = [agent for agent in agent.group.agent_set.all() if len(
                CompetitionAgent.objects.filter(agent=agent, round=competition.round_set.first())) == 1]

            numbers = dict(settings.NUMBER_AGENTS_BY_COMPETITION_TYPE)

            if numbers[competition.type_of_competition] <= len(groups_agents_in_round):
                return Response({'status': 'Reached the limit of agents',
                                 'message': 'Reached the number of competition_agents!'},
                                status=status.HTTP_400_BAD_REQUEST)

            # not modified values
            competition = get_object_or_404(Competition.objects.all(),
                name=serializer.validated_data['competition_name'])
            agent = get_object_or_404(Agent.objects.all(), agent_name=serializer.validated_data['agent_name'])

            CompetitionAgent.objects.create(agent=agent, round=competition.round_set.first(), competition=competition)

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': 'We cound not associate the agent to the competition.'},
                        status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        B{Delete} the associated agent from the round
        B{URL:} ../api/v1/competitions/associate_agent/<agent_name>/?competition_name?<competition_name>

        @type  competition_name: str
        @param competition_name: The competition name
        @type  agent_name: str
        @param agent_name: The agent name
        """
        if 'competition_name' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?competition_name=*competition_name*'},
                            status=status.HTTP_400_BAD_REQUEST)

        agent = get_object_or_404(Agent.objects.all(), agent_name=kwargs.get('pk'))
        competition = get_object_or_404(Competition.objects.all(), name=request.GET.get('competition_name', ''))

        if competition.state_of_competition != "Register":
            return Response({'status': 'Not allowed',
                             'message': 'The competition is not accepting agents.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        if len(GroupMember.objects.filter(group=agent.group, account=request.user)) != 1:
            return Response({'status': 'Permission denied',
                             'message': 'You must be part of the group.'},
                            status=status.HTTP_403_FORBIDDEN)

        if len(GroupEnrolled.objects.filter(group=agent.group, competition=competition)) != 1:
            return Response({'status': 'Permission denied',
                             'message': 'The group must first enroll in the competition.'},
                            status=status.HTTP_403_FORBIDDEN)

        # not modified values
        competition = get_object_or_404(Competition.objects.all(), name=request.GET.get('competition_name', ''))
        agent = get_object_or_404(Agent.objects.all(), agent_name=kwargs.get('pk'))

        competition_agent = CompetitionAgent.objects.filter(competition=competition,
                                                            round=competition.round_set.first(), agent=agent)
        competition_agent.delete()

        return Response({'status': 'Deleted',
                         'message': 'The competition agent has been deleted!'},
                        status=status.HTTP_200_OK)


class AssociateAgentAdmin(mixins.DestroyModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = CompetitionAgent.objects.all()
    serializer_class = RoundAgentSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(), IsAdmin(),

    def create(self, request, *args, **kwargs):
        """
        B{Associate} an agent
        B{URL:} ../api/v1/competitions/associate_agent_admin/

        @type  round_name: str
        @param round_name: The round name
        @type  agent_name: str
        @param agent_name: The agent name
        """

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            r = get_object_or_404(Round.objects.all(), name=serializer.validated_data['round_name'])
            agent = get_object_or_404(Agent.objects.all(), agent_name=serializer.validated_data['agent_name'])
            competition = r.parent_competition

            if len(GroupEnrolled.objects.filter(group=agent.group, competition=competition, valid=True)) != 1:
                return Response({'status': 'Permission denied',
                                 'message': 'The group must first enroll and with inscription valid.'},
                                status=status.HTTP_403_FORBIDDEN)

            # code valid
            if not agent.is_virtual and not agent.code_valid:
                return Response({'status': 'The agent code is not valid!',
                                 'message': 'Please submit a valid code first!'},
                                status=status.HTTP_400_BAD_REQUEST)

            # verify limits
            groups_agents_in_round = [agent for agent in agent.group.agent_set.all() if
                                      len(CompetitionAgent.objects.filter(agent=agent, round=r)) == 1]

            numbers = dict(settings.NUMBER_AGENTS_BY_COMPETITION_TYPE)

            if numbers[competition.type_of_competition] <= len(groups_agents_in_round):
                return Response({'status': 'Reached the limit of agents',
                                 'message': 'Reached the number of competition_agents!'},
                                status=status.HTTP_400_BAD_REQUEST)

            # not modified values
            r = get_object_or_404(Round.objects.all(), name=serializer.validated_data['round_name'])
            agent = get_object_or_404(Agent.objects.all(), agent_name=serializer.validated_data['agent_name'])
            competition = r.parent_competition

            CompetitionAgent.objects.create(agent=agent, round=r, competition=competition)

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': 'We cound not associate the agent to the competition.'},
                        status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        B{Delete} the associated agent from the round
        B{URL:} ../api/v1/competitions/associate_agent_admin/<agent_name>/

        @type  round_name: str
        @param round_name: The round name
        @type  agent_name: str
        @param agent_name: The agent name
        """
        r = get_object_or_404(Round.objects.all(), name=request.data.get('round_name', ''))
        agent = get_object_or_404(Agent.objects.all(), agent_name=kwargs.get('pk'))
        competition = r.parent_competition

        if len(GroupEnrolled.objects.filter(group=agent.group, competition=competition)) != 1:
            return Response({'status': 'Permission denied',
                             'message': 'The group must first enroll in the competition.'},
                            status=status.HTTP_403_FORBIDDEN)

        # not modified values
        r = get_object_or_404(Round.objects.all(), name=request.data.get('round_name', ''))
        agent = get_object_or_404(Agent.objects.all(), agent_name=kwargs.get('pk'))
        competition = r.parent_competition

        competition_agent = CompetitionAgent.objects.filter(competition=competition, round=r, agent=agent)
        competition_agent.delete()

        return Response({'status': 'Deleted',
                         'message': 'The competition agent has been deleted!'},
                        status=status.HTTP_200_OK)


class AgentsAssociated(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the list of agents by competition and group_name
        B{URL:} ../api/v1/competitions/agents_by_competition_group/<group_name>/?competition_name=<competition_name>

        @type  group_name: str
        @param group_name: The group name
        @type  competition_name: str
        @param competition_name: The competition name
        """
        group = get_object_or_404(Group.objects.all(), name=kwargs.get('pk'))
        competition = get_object_or_404(Competition.objects.all(), name=request.GET.get('competition_name', ''))

        agents = []
        for group_agent in group.agent_set.all():
            if len(CompetitionAgent.objects.filter(competition=competition, agent=group_agent)) > 0:
                agents += [group_agent]

        serializer = self.serializer_class([AgentSimplex(agent) for agent in agents], many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)