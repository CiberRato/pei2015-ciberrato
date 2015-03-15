import json

from django.shortcuts import get_object_or_404
from competition.models import Round, GroupEnrolled, CompetitionAgent, Agent
from competition.serializers import AgentSerializer, CompetitionAgentSerializer
from authentication.models import Group, GroupMember
from rest_framework import permissions
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from django.core.files.storage import default_storage
from groups.permissions import IsAdminOfGroup
from django.conf import settings
from competition.views.simplex import AgentSimplex


class AgentViewSets(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                    mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),
        return permissions.IsAuthenticated(), IsAdminOfGroup(),

    def create(self, request, *args, **kwargs):
        """
        B{Create} an agent
        B{URL:} ../api/v1/competitions/agent/

        @type  agent_name: str
        @param agent_name: The agent name
        @type  group_name: str
        @param group_name: The group name
        @type  is_virtual: boolean
        @param is_virtual: True if is virtual or False if is not virtual
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = request.user
            group = get_object_or_404(Group.objects.all(), name=serializer.validated_data['group_name'])
            agent_name = serializer.validated_data['agent_name']
            Agent.objects.create(agent_name=agent_name, user=user, group=group,
                                 is_virtual=serializer.validated_data['is_virtual'])

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': 'The agent could not be created with received data'},
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} information of the agent
        B{URL:} ../api/v1/competitions/agent/<agent_name>/

        @type  agent_name: str
        @param agent_name: The agent name
        """
        agent = get_object_or_404(self.queryset, agent_name=kwargs.get('pk'))
        serializer = AgentSerializer(AgentSimplex(agent))

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} an agent
        B{URL:} ../api/v1/competitions/agent/<agent_name>/

        @type  agent_name: str
        @param agent_name: The agent name
        """
        agent = get_object_or_404(self.queryset, agent_name=kwargs.get('pk'))

        if agent.locations:
            if len(json.loads(agent.locations)) > 0:
                for path in json.loads(agent.locations):
                    default_storage.delete(path)

        agent.delete()

        return Response({'status': 'Deleted',
                         'message': 'The agent has been deleted'},
                        status=status.HTTP_200_OK)


class AssociateAgent(mixins.DestroyModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = CompetitionAgent.objects.all()
    serializer_class = CompetitionAgentSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def create(self, request, *args, **kwargs):
        """
        B{Associate} an agent
        B{URL:} ../api/v1/competitions/associate_agent/

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

            if competition.state_of_competition != "Register":
                return Response({'status': 'Not allowed',
                                 'message': 'The group is not accepting agents.'},
                                status=status.HTTP_401_UNAUTHORIZED)

            group_member = GroupMember.objects.filter(group=agent.group, account=request.user)
            if len(group_member) != 1:
                return Response({'status': 'Permission denied',
                                 'message': 'You must be part of the group.'},
                                status=status.HTTP_403_FORBIDDEN)

            group_enrolled = GroupEnrolled.objects.filter(group=agent.group, competition=competition)
            if len(group_enrolled) != 1:
                return Response({'status': 'Permission denied',
                                 'message': 'The group must first enroll in the competition.'},
                                status=status.HTTP_403_FORBIDDEN)

            # code valid
            if not agent.is_virtual and not agent.code_valid:
                return Response({'status': 'The agent code is not valid!',
                                 'message': 'Please submit a valid code first!'},
                                status=status.HTTP_400_BAD_REQUEST)

            # verify limits
            groups_agent = Agent.objects.filter(group=agent.group)
            groups_agents_in_round = [agent for agent in groups_agent if
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
        B{URL:} ../api/v1/competitions/associate_agent/<agent_name>/?round_name?<round_name>

        @type  round_name: str
        @param round_name: The round name
        @type  agent_name: str
        @param agent_name: The agent name
        """
        if 'round_name' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?round_name=*round_name*'},
                            status=status.HTTP_400_BAD_REQUEST)

        r = get_object_or_404(Round.objects.all(), name=request.GET.get('round_name', ''))
        agent = get_object_or_404(Agent.objects.all(), agent_name=kwargs.get('pk'))
        competition = r.parent_competition

        if competition.state_of_competition != "Register":
            return Response({'status': 'Not allowed',
                             'message': 'The group is not accepting agents.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        group_member = GroupMember.objects.filter(group=agent.group, account=request.user)
        if len(group_member) != 1:
            return Response({'status': 'Permission denied',
                             'message': 'You must be part of the group.'},
                            status=status.HTTP_403_FORBIDDEN)

        group_enrolled = GroupEnrolled.objects.filter(group=agent.group, competition=competition)
        if len(group_enrolled) != 1:
            return Response({'status': 'Permission denied',
                             'message': 'The group must first enroll in the competition.'},
                            status=status.HTTP_403_FORBIDDEN)

        # not modified values
        r = get_object_or_404(Round.objects.all(), name=request.GET.get('round_name', ''))
        agent = get_object_or_404(Agent.objects.all(), agent_name=kwargs.get('pk'))
        competition = r.parent_competition

        competition_agent = CompetitionAgent.objects.filter(competition=competition, round=r, agent=agent)
        competition_agent.delete()

        return Response({'status': 'Deleted',
                         'message': 'The competition agent has been deleted!'},
                        status=status.HTTP_200_OK)


class AgentsByGroupViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the list of agents by group
        B{URL:} ../api/v1/competitions/agents_by_group/<group_name>/

        @type  group_name: str
        @param group_name: The group name
        """
        group = get_object_or_404(Group.objects.all(), name=kwargs.get('pk'))
        agents = Agent.objects.filter(group=group)
        serializer = self.serializer_class([AgentSimplex(agent) for agent in agents], many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)