import json

from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response

from django.core.files.storage import default_storage

from ..models import Agent
from ..serializers import AgentSerializer, AgentCodeValidationSerializer
from ..simplex import AgentSimplex

from authentication.models import Group, Account
from groups.permissions import IsAdminOfGroup
from competition.serializers import CompetitionSerializer


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
        B{URL:} ../api/v1/agents/agent/

        @type  agent_name: str
        @param agent_name: The agent name
        @type  group_name: str
        @param group_name: The group name
        @type  is_local: boolean
        @param is_local: True if is virtual or False if is not virtual
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = request.user
            group = get_object_or_404(Group.objects.all(), name=serializer.validated_data['group_name'])
            agent_name = serializer.validated_data['agent_name']

            if serializer.validated_data['is_local']:
                Agent.objects.create(agent_name=agent_name, user=user, group=group, code_valid=True,
                                     is_local=serializer.validated_data['is_local'])
            else:
                Agent.objects.create(agent_name=agent_name, user=user, group=group,
                                     is_local=serializer.validated_data['is_local'])

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} information of the agent
        B{URL:} ../api/v1/agents/agent/<agent_name>/

        @type  agent_name: str
        @param agent_name: The agent name
        """
        agent = get_object_or_404(self.queryset, agent_name=kwargs.get('pk'))
        serializer = AgentSerializer(AgentSimplex(agent))

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} an agent
        B{URL:} ../api/v1/agents/agent/<agent_name>/

        @type  agent_name: str
        @param agent_name: The agent name
        """
        agent = get_object_or_404(self.queryset, agent_name=kwargs.get('pk'))
        agent.delete()

        return Response({'status': 'Deleted',
                         'message': 'The agent has been deleted'},
                        status=status.HTTP_200_OK)


class AgentsByGroupViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the list of agents by group
        B{URL:} ../api/v1/agents/agents_by_group/<group_name>/

        @type  group_name: str
        @param group_name: The group name
        """
        group = get_object_or_404(Group.objects.all(), name=kwargs.get('pk'))
        serializer = self.serializer_class([AgentSimplex(agent) for agent in group.agent_set.all()], many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class AgentsByUserViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the list of agents by username
        B{URL:} ../api/v1/agents/agents_by_user/<username>/

        @type  username: str
        @param username: The user name
        """
        user = get_object_or_404(Account.objects.all(), username=kwargs.get('pk'))
        serializer = self.serializer_class([AgentSimplex(agent) for agent in user.agent_set.all()], many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class AgentCompetitionAssociated(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Agent.objects.all()
    serializer_class = CompetitionSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the list of competitions that agent is associated
        B{URL:} ../api/v1/agents/agent_competitions/<agent_name>/

        @type  agent_name: str
        @param agent_name: The agent name
        """

        agent = get_object_or_404(Agent.objects.all(), username=kwargs.get('pk'))
        serializer = self.serializer_class([ac.competition for ac in agent.competitionagent_set], many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class AgentCodeValidation(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentCodeValidationSerializer

    def update(self, request, *args, **kwargs):
        """
        B{Update} the code validation attributes
        B{URL:} ../api/v1/agents/code_validation/<agent_name>/

        @type  agent_name: str
        @param agent_name: The agent name

        @type  code_valid: bool
        @param code_valid: True or False
        @type  validation_result: str
        @param validation_result: The validation result
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            agent = get_object_or_404(Agent.objects.all(), agent_name=kwargs.get('pk'))

            agent.code_valid = serializer.validated_data['code_valid']
            agent.validation_result = serializer.validated_data['validation_result']
            agent.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)