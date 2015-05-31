from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.files import File
from django.db import IntegrityError
from django.db import transaction
import os

from rest_framework import permissions
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response

import requests

from ..models import Agent, AgentFile
from ..serializers import AgentSerializer, AgentCodeValidationSerializer, SubmitCodeAgentSerializer
from ..simplex import AgentSimplex

from authentication.models import Team, Account
from teams.permissions import IsAdminOfTeam, MustBeTeamMember
from competition.serializers import CompetitionSerializer
from competition.models import TypeOfCompetition, Competition, CompetitionAgent, LogTrialAgent

from notifications.models import NotificationTeam


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
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            team = get_object_or_404(Team.objects.all(), name=serializer.validated_data['team_name'])
            agent_name = serializer.validated_data['agent_name']

            if agent_name == 'Remote':
                return Response({'status': 'Bad Request',
                                 'message': 'Remote is a reserved name for the Agent, that agents are \
                                 automatically created for competitions that allow remote agents!'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                with transaction.atomic():
                    agent = Agent.objects.create(agent_name=agent_name, user=request.user, team=team,
                                                 language=serializer.validated_data['language'])
                    directory = os.path.join(settings.BASE_DIR, "static/samples/"+agent.language+"/")

                    only_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
                    for f in only_files:
                        if f != '.DS_Store':
                            f_a = AgentFile.objects.create(agent=agent, original_name=f)
                            f_a.file.save(f, File(open(directory + f), 'rb'))
                            f_a.save()
            except IntegrityError:
                return Response({'status': 'Bad request',
                                 'message': 'The team has already one agent with that name!'},
                                status=status.HTTP_400_BAD_REQUEST)

            # when the agent is created sends notification to the team
            NotificationTeam.add(team=team, status="info",
                                 message="You have a new agent in your team " + team.name + "!")

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} information of the agent
        B{URL:} ../api/v1/agents/agent/<agent_name>/?team_name=<team_name>

        -> Permissions
        # TeamMember
            The current logged user must be one team member

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
        MustBeTeamMember(user=request.user, team=team)

        serializer = AgentSerializer(AgentSimplex(agent))

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} an agent
        B{URL:} ../api/v1/agents/agent/<agent_name>/?team_name=<team_name>

        -> Permissions
        # TeamMember
            The current logged user must be one team member

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
        MustBeTeamMember(user=request.user, team=team)

        agent = get_object_or_404(Agent.objects.all(), team=team, agent_name=kwargs.get('pk'))

        if agent.is_remote:
            return Response({'status': 'Bad request',
                             'message': 'You can not remove a Remove agent!'},
                            status=status.HTTP_400_BAD_REQUEST)

        # when the agent is deleted sends notification to the team
        NotificationTeam.add(team=team, status="info",
                             message="The agent " + agent.agent_name + " has been removed!")

        # if is enrolled in some competition != solo trials or hall of fame cant't be deleted
        # when the agent is deleted it must delete the solo trials and participations in hall of fame
        try:
            private_competition_type = TypeOfCompetition.objects.get(name=settings.PRIVATE_COMPETITIONS_NAME)

            for cp in agent.competitionagent_set.all():
                if cp.competition.type_of_competition.name != settings.PRIVATE_COMPETITIONS_NAME and cp.competition.type_of_competition.name != settings.HALL_OF_FAME_START_STR + 'Single':
                    return Response({'status': 'Bad request',
                                     'message': 'You can not remove this agent, participated in some competitions!'},
                                    status=status.HTTP_400_BAD_REQUEST)

            for cp in agent.competitionagent_set.all():
                if cp.competition.type_of_competition == private_competition_type:
                    cp.delete()
        except TypeOfCompetition.DoesNotExist:
            pass

        hall_of_fame = Competition.get_hall_fame()
        try:
            cp = CompetitionAgent.objects.get(competition=hall_of_fame, agent=agent)
            for cp_trial in cp.logtrialagent_set.all():
                cp_trial.trial.delete()
                cp_trial.delete()
        except CompetitionAgent.DoesNotExist:
            pass

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


class AgentsByTeamValidViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the list of agents by team with the code valid
        B{URL:} ../api/v1/agents/agents_valid_by_team/<team_name>/

        :type  team_name: str
        :param team_name: The team name
        """
        team = get_object_or_404(Team.objects.all(), name=kwargs.get('pk'))
        serializer = self.serializer_class([AgentSimplex(agent) for agent in team.agent_set.all()
                                            if agent.code_valid], many=True)

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
        agents = Agent.objects.filter(team=user.teams.all())
        serializer = self.serializer_class([AgentSimplex(agent) for agent in agents], many=True)

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

        -> Permissions
        # TeamMember
            The current logged user must be one team member

        :type  team_name: str
        :param team_name: The team name
        :type  agent_name: str
        :param agent_name: The agent name
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            team = get_object_or_404(Team.objects.all(), name=serializer.validated_data['team_name'])
            MustBeTeamMember(team=team, user=request.user)
            agent = get_object_or_404(Agent.objects.all(), team=team,
                                      agent_name=serializer.validated_data['agent_name'])

            # call code validations
            try:
                requests.get(settings.TEST_CODE_ENDPOINT.replace("<agent_name>",
                                                                 agent.agent_name).replace("<team_name>",
                                                                                           agent.team.name))
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

        SERVER-TO-SERVER

        :type  agent_name: str
        :param agent_name: The agent name

        data:
        :type  team_name: str
        :param team_name: The team name
        :type  code_valid: bool
        :param code_valid: True or False
        :type  validation_result: str
        :param validation_result: The validation result
        :type  validation_execution_log: str
        :param validation_execution_log: The validation execution log result
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            team = get_object_or_404(Team.objects.all(), name=serializer.validated_data['team_name'])
            agent = get_object_or_404(Agent.objects.all(), agent_name=kwargs.get('pk'), team=team)

            agent.code_valid = serializer.validated_data['code_valid']
            agent.validation_result = serializer.validated_data['validation_result']

            if 'validation_execution_log' in serializer.validated_data:
                agent.validation_execution_log = serializer.validated_data['validation_execution_log']
            agent.save()

            if agent.validation_result:
                NotificationTeam.add(team=team, status="ok", message=agent.validation_result, trigger="code_valid")
            else:
                NotificationTeam.add(team=team, status="error", message=agent.validation_result, trigger="code_valid")

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)