from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from django.conf import settings

import requests

from ..models import Agent
from ..serializers import AgentSerializer, AgentCodeValidationSerializer, SubmitCodeAgentSerializer
from ..simplex import AgentSimplex

from authentication.models import Team, Account, TeamMember
from teams.permissions import IsAdminOfTeam
from competition.serializers import CompetitionSerializer


class AgentViewSets(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                    mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),
        return permissions.IsAuthenticated(), IsAdminOfTeam(),

    def create(self, request, *args, **kwargs):
        """
        B{Create} an agent
        B{URL:} ../api/v1/agents/agent/

        :type  agent_name: str
        :param agent_name: The agent name
        :type  team_name: str
        :param team_name: The team name
        :type  is_remote: boolean
        :param is_remote: True if is virtual or False if is not virtual
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = request.user
            team = get_object_or_404(Team.objects.all(), name=serializer.validated_data['team_name'])
            agent_name = serializer.validated_data['agent_name']

            Agent.objects.create(agent_name=agent_name, user=user, team=team,
                                 language=serializer.validated_data['language'])

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} information of the agent
        B{URL:} ../api/v1/agents/agent/<agent_name>/?team_name=<team_name>

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
        serializer = AgentSerializer(AgentSimplex(agent))

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} an agent
        B{URL:} ../api/v1/agents/agent/<agent_name>/?team_name=<team_name>

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
        agent.delete()

        return Response({'status': 'Deleted',
                         'message': 'The agent has been deleted'},
                        status=status.HTTP_200_OK)


class AgentsByTeamViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the list of agents by team
        B{URL:} ../api/v1/agents/agents_by_team/<team_name>/

        :type  team_name: str
        :param team_name: The team name
        """
        team = get_object_or_404(Team.objects.all(), name=kwargs.get('pk'))
        serializer = self.serializer_class([AgentSimplex(agent) for agent in team.agent_set.all()], many=True)

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

        :type  username: str
        :param username: The user name
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
        B{URL:} ../api/v1/agents/agent_competitions/<agent_name>/?team_name=<team_name>

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
        agent = get_object_or_404(Agent.objects.all(), agent_name=kwargs.get('pk'), team=team)
        serializer = self.serializer_class([ac.competition for ac in agent.competitionagent_set], many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SubmitCodeForValidation(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Agent.objects.all()
    serializer_class = SubmitCodeAgentSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def create(self, request, *args, **kwargs):
        """
        B{POST} validate code
        B{URL:} ../api/v1/agents/validate_code/

        :type  team_name: str
        :param team_name: The team name
        :type  agent_name: str
        :param agent_name: The agent name
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            team = get_object_or_404(Team.objects.all(), name=serializer.validated_data['team_name'])
            agent = get_object_or_404(Agent.objects.all(), team=team,
                                      agent_name=serializer.validated_data['agent_name'])

            if len(TeamMember.objects.filter(team=agent.team, account=request.user)) == 0:
                return Response({'status': 'Permission denied',
                                 'message': 'You must be part of the team.'},
                                status=status.HTTP_403_FORBIDDEN)

            # call code validations
            try:
                requests.get(settings.TEST_CODE_ENDPOINT.replace("<agent_name>", agent.agent_name))
                agent.code_valid = False
                agent.validation_result = "submitted"
            except requests.ConnectionError:
                agent.code_valid = False
                agent.validation_result = "The endpoint to do the code validation is down!"
            agent.save()

            return Response({'status': 'OK',
                             'message': 'The code has been submitted for validation!'},
                            status=status.HTTP_200_OK)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class AgentCodeValidation(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentCodeValidationSerializer

    def update(self, request, *args, **kwargs):
        """
        B{Update} the code validation attributes
        B{URL:} ../api/v1/agents/code_validation/<agent_name>/

        :type  agent_name: str
        :param agent_name: The agent name

        data:
        :type  team_name: str
        :param team_name: The team name
        :type  code_valid: bool
        :param code_valid: True or False
        :type  validation_result: str
        :param validation_result: The validation result
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            team = get_object_or_404(Team.objects.all(), name=serializer.validated_data['team_name'])
            agent = get_object_or_404(Agent.objects.all(), agent_name=kwargs.get('pk'), team=team)

            agent.code_valid = serializer.validated_data['code_valid']
            agent.validation_result = serializer.validated_data['validation_result']
            agent.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)