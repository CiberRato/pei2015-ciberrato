from django.shortcuts import get_object_or_404
from competition.models import Competition, Round, Simulation, GroupEnrolled, CompetitionAgent, Agent
from competition.serializers import CompetitionSerializer, RoundSerializer, SimulationSerializer, \
    GroupEnrolledSerializer, AgentSerializer, CompetitionAgentSerializer
from django.db import IntegrityError
from django.db import transaction
from authentication.models import Group, GroupMember
from authentication.serializers import AccountSerializer

from groups.serializers import GroupSerializer

from rest_framework import permissions
from rest_framework import mixins, viewsets, views, status

from rest_framework.decorators import api_view
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from competition.permissions import IsAdmin
from groups.permissions import IsAdminOfGroup

from django.conf import settings
import json
import os.path


class RoundSimplex:
    def __init__(self, r):
        self.name = r.name
        self.parent_competition_name = str(r.parent_competition)
        self.param_list_path = r.param_list_path
        self.grid_path = r.grid_path
        self.lab_path = r.lab_path
        self.agents_list = r.agents_list


class GroupEnrolledSimplex:
    def __init__(self, ge):
        self.competition_name = ge.competition.name
        self.group_name = ge.group.name


class AgentSimplex:
    def __init__(self, ag):
        self.agent_name = ag.agent_name
        self.user = ag.user
        self.is_virtual = ag.is_virtual
        self.language = ag.language
        self.competitions = ag.competitions

        self.rounds = []
        for r in ag.rounds.all():
            self.rounds += [RoundSimplex(r)]

        self.group_name = ag.group.name
        self.created_at = ag.created_at
        self.updated_at = ag.updated_at


class CompetitionAgentSimplex:
    def __init__(self, cas):
        self.round_name = cas.round.name
        self.agent_name = cas.agent.agent_name
        self.created_at = cas.created_at
        self.updated_at = cas.updated_at


class CompetitionViewSet(viewsets.ModelViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),
        return permissions.IsAuthenticated(), IsAdmin(),

    def create(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            Competition.objects.create(**serializer.validated_data)

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': 'The competitions could not be created with received data'},
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk, **kwargs):
        queryset = Competition.objects.all()
        competition = get_object_or_404(queryset, name=pk)
        serializer = self.serializer_class(competition)

        return Response(serializer.data)

    def destroy(self, request, pk, **kwargs):
        queryset = Competition.objects.all()
        competition = get_object_or_404(queryset, name=pk)

        rounds = Round.objects.filter(parent_competition=competition)
        for r in rounds:
            r.delete()

        competition.delete()

        return Response({'status': 'Deleted',
                         'message': 'The competition has been deleted'},
                        status=status.HTTP_200_OK)


class CompetitionGetGroupsViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = GroupSerializer

    def retrieve(self, request, pk, **kwargs):
        """
        B{Retrieve} the list of a Groups enrolled and with valid inscription in the Competition
        B{URL:} ../api/v1/competitions/groups/<competition_name>/

        @type  competition_name: str
        @param competition_name: The competition name
        """
        competition = get_object_or_404(Competition.objects.all(), name=pk)
        valid = GroupEnrolled.objects.filter(valid=True, competition=competition)
        valid_groups = [g.group for g in valid]
        serializer = self.serializer_class(valid_groups, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CompetitionGetNotValidGroupsViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = GroupSerializer

    def retrieve(self, request, pk, **kwargs):
        """
        B{Retrieve} the list of a Groups enrolled with inscription not valid in the Competition
        B{URL:} ../api/v1/competitions/groups_not_valid/<competition_name>/

        @type  competition_name: str
        @param competition_name: The competition name
        """
        competition = get_object_or_404(Competition.objects.all(), name=pk)
        not_valid = GroupEnrolled.objects.filter(valid=False, competition=competition)
        not_valid_groups = [g.group for g in not_valid]
        serializer = self.serializer_class(not_valid_groups, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CompetitionGroupValidViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = GroupEnrolled.objects.all()
    serializer_class = GroupEnrolledSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(), IsAdmin(),

    def update(self, request, pk, **kwargs):
        """
        B{Update} the group enrolled attribute to valid or to false (it's a toggle)
        B{URL:} ../api/v1/competitions/group_valid/<group_name>/?competition_name=<competition_name>

        @type  competition_name: str
        @param competition_name: The competition name
        @type  group_name: str
        @param group_name: The group name
        """
        if 'competition_name' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?competition_name=<competition_name>'},
                            status=status.HTTP_400_BAD_REQUEST)

        competition = get_object_or_404(Competition.objects.all(),
                                        name=request.GET.get('competition_name', ''))
        group = get_object_or_404(Group.objects.all(),
                                  name=pk)

        group_enrolled = get_object_or_404(GroupEnrolled.objects.all(), group=group, competition=competition)
        group_enrolled.valid = not group_enrolled.valid
        group_enrolled.save()

        return Response({'status': 'Updated',
                         'message': 'The group inscription has been updated to ' + str(group_enrolled.valid) + ' .'},
                        status=status.HTTP_200_OK)


class CompetitionOldestRoundViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = RoundSerializer
    queryset = Round.objects.all()

    def retrieve(self, request, pk, **kwargs):
        """
        B{Get} the oldest round competition
        B{URL:} ../api/v1/competitions/first_round/<competition_name>/

        @type  competition_name: str
        @param competition_name: The competition name
        """
        competition = get_object_or_404(Competition.objects.all(), name=pk)
        competition_rounds = Round.objects.filter(parent_competition=competition)

        if len(competition_rounds) == 0:
            return Response({'status': 'Bad request',
                             'message': 'Not found '},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(RoundSimplex(competition_rounds.reverse()[0]))

        return Response(serializer.data, status=status.HTTP_200_OK)


class CompetitionEarliestRoundViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = RoundSerializer
    queryset = Round.objects.all()

    def retrieve(self, request, pk, **kwargs):
        """
        B{Get} the earliest round competition
        B{URL:} ../api/v1/competitions/earliest_round/<competition_name>/

        @type  competition_name: str
        @param competition_name: The competition name
        """
        competition = get_object_or_404(Competition.objects.all(), name=pk)
        competition_rounds = Round.objects.filter(parent_competition=competition)

        if len(competition_rounds) == 0:
            return Response({'status': 'Bad request',
                             'message': 'Not found '},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(RoundSimplex(competition_rounds[0]))

        return Response(serializer.data, status=status.HTTP_200_OK)


class RoundViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                   mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Round.objects.all()
    serializer_class = RoundSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),
        return permissions.IsAuthenticated(), IsAdmin(),

    def list(self, request, **kwargs):
        serializer = self.serializer_class([RoundSimplex(r=query) for query in Round.objects.all()], many=True)
        return Response(serializer.data)

    def create(self, request, **kwargs):
        """
        B{Create} a Round
        B{URL:} ../api/v1/competitions/round/

        @type  name: str
        @param name: The round name
        @type  parent_competition_name: str
        @param parent_competition_name: The competition parent name
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            competition = get_object_or_404(Competition.objects.all(),
                                            name=serializer.validated_data['parent_competition_name'])

            Round.objects.create(name=serializer.validated_data['name'], parent_competition=competition)

            return Response({'status': 'Created',
                             'message': 'The round has been created.'},
                            status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad request',
                         'message': 'The round could not be created with received data.'},
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk, **kwargs):
        """
        B{Get} the oldest round competition
        B{URL:} ../api/v1/competitions/round/<round_name>/

        @type  round_name: str
        @param round_name: The round name
        """
        r = get_object_or_404(Round.objects.all(), name=pk)

        serializer = self.serializer_class(RoundSimplex(r))

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk, **kwargs):
        """
        B{Remove} a round from the competition
        B{URL:} ../api/v1/competitions/round/<name>/

        @type  name: str
        @param name: The round name
        """
        r = get_object_or_404(Round.objects.all(), name=pk)

        for c_agent in CompetitionAgent.objects.all():
            c_agent.delete()

        r.delete()

        return Response(status=status.HTTP_200_OK)


class EnrollGroup(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                  mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = GroupEnrolled.objects.all()
    serializer_class = GroupEnrolledSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),
        return permissions.IsAuthenticated(), IsAdminOfGroup(),

    def list(self, request, **kwargs):
        serializer = self.serializer_class([GroupEnrolledSimplex(ge=query) for query in GroupEnrolled.objects.all()],
                                           many=True)
        return Response(serializer.data)

    def create(self, request, **kwargs):
        """
        B{Create} a Group Enrolled to a competition
        B{URL:} ../api/v1/competitions/enroll/

        @type  competition_name: str
        @param competition_name: The Competition name
        @type  group_name: str
        @param group_name: The Group name
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            competition = get_object_or_404(Competition.objects.all(),
                                            name=serializer.validated_data['competition_name'])
            group = get_object_or_404(Group.objects.all(),
                                      name=serializer.validated_data['group_name'])

            if competition.state_of_competition != "Register":
                return Response({'status': 'Not allowed',
                                 'message': 'The group can\'t enroll in the competition.'},
                                status=status.HTTP_401_UNAUTHORIZED)
            try:
                with transaction.atomic():
                    GroupEnrolled.objects.create(competition=competition, group=group)
            except IntegrityError:
                return Response({'status': 'Bad request',
                                 'message': 'The group already enrolled.'},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response({'status': 'Created',
                             'message': 'The group has enrolled.'},
                            status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad request',
                         'message': 'The group can\'t enroll with received data.'},
                        status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk, **kwargs):
        """
        B{Remove} a group from the competition
        B{URL:} ../api/v1/competitions/enroll/<competition_name>/?group_name=<group_name>

        @type  competition_name: str
        @param competition_name: The competition name
        @type  group_name: str
        @param group_name: The group name
        """
        if 'group_name' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?group_name=*group_name*'},
                            status=status.HTTP_400_BAD_REQUEST)

        competition = get_object_or_404(Competition.objects.all(), name=pk)
        group = get_object_or_404(Group.objects.all(), name=request.GET.get('group_name', ''))

        group_not_enrolled = (len(GroupEnrolled.objects.filter(competition=competition, group=group)) == 0)

        if group_not_enrolled:
            return Response({'status': 'Bad request',
                             'message': 'The group is not enrolled in the competition'},
                            status=status.HTTP_400_BAD_REQUEST)

        group_enrolled = GroupEnrolled.objects.get(competition=competition, group=group)
        group_enrolled.delete()

        return Response(status=status.HTTP_200_OK)


class AgentViewSets(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                    mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),
        return permissions.IsAuthenticated(), IsAdminOfGroup(),

    def create(self, request, *args, **kwargs):
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

    def retrieve(self, request, pk, **kwargs):
        """
        B{Get} information of the agent
        B{URL:} ../api/v1/competitions/agent/<agent_name>/

        @type  agent_name: str
        @param agent_name: The agent name
        """
        agent = get_object_or_404(Agent.objects.all(), agent_name=pk)
        serializer = AgentSerializer(AgentSimplex(agent))

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk, **kwargs):
        """
        B{Destroy} an agent
        B{URL:} ../api/v1/competitions/agent/<agent_name>/

        @type  agent_name: str
        @param agent_name: The agent name
        """
        agent = get_object_or_404(Agent.objects.all(), agent_name=pk)

        if agent.locations:
            if len(json.loads(agent.locations)) > 0:
                for path in json.loads(agent.locations):
                    default_storage.delete(path)

        agent.delete()

        return Response({'status': 'Deleted',
                         'message': 'The agent has been deleted'},
                        status=status.HTTP_200_OK)


class AgentsRound(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = CompetitionAgent.objects.all()
    serializer_class = CompetitionAgentSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, pk, **kwargs):
        """
        B{Get} the agents available to compete in the round
        B{URL:} ../api/v1/competitions/valid_round_agents/<round_name>/

        @type  round_name: str
        @param round_name: The round name
        """
        r = get_object_or_404(Round.objects.all(), name=pk)
        competition_agents = CompetitionAgent.objects.filter(round=r, eligible=True)
        competition_agents = [CompetitionAgentSimplex(agent) for agent in competition_agents]
        serializer = self.serializer_class(competition_agents, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class AgentsNotEligible(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = CompetitionAgent.objects.all()
    serializer_class = CompetitionAgentSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, pk, **kwargs):
        """
        B{Get} the agents available to compete in the round
        B{URL:} ../api/v1/competitions/not_eligible_round_agents/<round_name>/

        @type  round_name: str
        @param round_name: The round name
        """
        r = get_object_or_404(Round.objects.all(), name=pk)
        competition_agents = CompetitionAgent.objects.filter(round=r, eligible=False)
        competition_agents = [CompetitionAgentSimplex(agent) for agent in competition_agents]
        serializer = self.serializer_class(competition_agents, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RoundParticipants(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = CompetitionAgent.objects.all()
    serializer_class = AccountSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, pk, **kwargs):
        """
        B{Get} the participants available to compete in the round
        B{URL:} ../api/v1/competitions/valid_round_participants/<round_name>/

        @type  round_name: str
        @param round_name: The round name
        """
        r = get_object_or_404(Round.objects.all(), name=pk)
        competition_agents = CompetitionAgent.objects.filter(round=r, eligible=True)
        competition_groups = [agent.agent.group for agent in competition_agents]
        accounts = []
        for group in competition_groups:
            group_members = GroupMember.objects.filter(group=group)
            accounts += [group_member.account for group_member in group_members]
        serializer = self.serializer_class(accounts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RoundParticipantsNotEligible(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = CompetitionAgent.objects.all()
    serializer_class = AccountSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, pk, **kwargs):
        """
        B{Get} the participants available to compete in the round
        B{URL:} ../api/v1/competitions/not_eligible_round_participants/<round_name>/

        @type  round_name: str
        @param round_name: The round name
        """
        r = get_object_or_404(Round.objects.all(), name=pk)
        competition_agents = CompetitionAgent.objects.filter(round=r, eligible=False)
        competition_groups = [agent.agent.group for agent in competition_agents]
        accounts = []
        for group in competition_groups:
            group_members = GroupMember.objects.filter(group=group)
            accounts += [group_member.account for group_member in group_members]
        serializer = self.serializer_class(accounts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RoundGroups(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = CompetitionAgent.objects.all()
    serializer_class = GroupSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, pk, **kwargs):
        """
        B{Get} the groups available to compete in the round
        B{URL:} ../api/v1/competitions/valid_round_groups/<round_name>/

        @type  round_name: str
        @param round_name: The round name
        """
        r = get_object_or_404(Round.objects.all(), name=pk)
        competition_agents = CompetitionAgent.objects.filter(round=r, eligible=True)
        competition_groups = [agent.agent.group for agent in competition_agents]
        serializer = self.serializer_class(competition_groups, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RoundGroupsNotEligible(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = CompetitionAgent.objects.all()
    serializer_class = GroupSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, pk, **kwargs):
        """
        B{Get} the groups available to compete in the round
        B{URL:} ../api/v1/competitions/not_eligible_round_groups/<round_name>/

        @type  round_name: str
        @param round_name: The round name
        """
        r = get_object_or_404(Round.objects.all(), name=pk)
        competition_agents = CompetitionAgent.objects.filter(round=r, eligible=False)
        competition_groups = [agent.agent.group for agent in competition_agents]
        serializer = self.serializer_class(competition_groups, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


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
            round = get_object_or_404(Round.objects.all(), name=serializer.validated_data['round_name'])
            agent = get_object_or_404(Agent.objects.all(), agent_name=serializer.validated_data['agent_name'])
            competition = round.parent_competition

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
                                      len(CompetitionAgent.objects.filter(agent=agent, round=round)) == 0]

            numbers = dict(settings.NUMBER_AGENTS_BY_COMPETITION_TYPE)

            if numbers[competition.type_of_competition] <= len(groups_agents_in_round):
                return Response({'status': 'Reached the limit of agents',
                                 'message': 'The group must first enroll in the competition.'},
                                status=status.HTTP_400_BAD_REQUEST)

            CompetitionAgent.objects.create(agent=agent, round=round, competition=competition)

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': 'We cound not associate the agent to the competition.'},
                        status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk, **kwargs):
        """
        B{Associate} an agent
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
        agent = get_object_or_404(Agent.objects.all(), agent_name=pk)
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

        competition_agent = CompetitionAgent.objects.filter(competition=competition, round=r, agent=agent)
        competition_agent.delete()

        return Response({'status': 'Deleted',
                         'message': 'The competition agent has been deleted!'},
                        status=status.HTTP_200_OK)


class DeleteUploadedFileAgent(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def destroy(self, request, pk, **kwargs):
        """
        B{Destroy} an agent file
        B{URL:} ../api/v1/competitions/delete_agent_file/<agent_name>/?file_name=<file_name>

        @type  agent_name: str
        @param agent_name: The agent name
        @type  file_name: str
        @param file_name: The file name
        """
        agent = get_object_or_404(Agent.objects.all(), agent_name=pk)
        group_member = GroupMember.objects.filter(group=agent.group, account=request.user)

        if len(group_member) == 0:
            return Response({'status': 'Permission denied',
                             'message': 'You must be part of the group.'},
                            status=status.HTTP_403_FORBIDDEN)

        if 'file_name' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?file_name=*file_name*'},
                            status=status.HTTP_400_BAD_REQUEST)

        if default_storage.exists('competition_files/agents/' + agent.agent_name + '/' + request.GET.get('file_name',
                                                                                                         '')):
            load = json.loads(agent.locations)
            load.remove('competition_files/agents/' + agent.agent_name + '/' + request.GET.get('file_name', ''))
            agent.locations = json.dumps(load)
            agent.save()
            default_storage.delete(
                'competition_files/agents/' + agent.agent_name + '/' + request.GET.get('file_name', ''))
            return Response({'status': 'Deleted',
                             'message': 'The agent file has been deleted'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'status': 'Not found',
                             'message': 'The agent file has not been found!'},
                            status=status.HTTP_404_NOT_FOUND)


class UploadAgent(views.APIView):
    parser_classes = (FileUploadParser,)

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def post(self, request):
        if 'agent_name' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?agent_name=*agent_name*'},
                            status=status.HTTP_400_BAD_REQUEST)

        if 'language' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?language=*language*'},
                            status=status.HTTP_400_BAD_REQUEST)

        allowed_languages = dict(settings.ALLOWED_UPLOAD_LANGUAGES).values()
        if request.GET.get('language', '') not in allowed_languages:
            return Response({'status': 'Bad request',
                             'message': 'The uploaded language is not allowed.'},
                            status=status.HTTP_400_BAD_REQUEST)

        agent = get_object_or_404(Agent.objects.all(), agent_name=request.GET.get('agent_name', ''))

        if agent.is_virtual:
            return Response({'status': 'Bad request',
                             'message': 'You can\'t upload code to a virtual agent!'},
                            status=status.HTTP_400_BAD_REQUEST)

        group_member = GroupMember.objects.filter(group=agent.group, account=request.user)

        if len(group_member) == 0:
            return Response({'status': 'Permission denied',
                             'message': 'You must be part of the group.'},
                            status=status.HTTP_403_FORBIDDEN)

        file_obj = request.data['file']

        # language agent
        agent.language = request.GET.get('language', '')

        if file_obj.size > settings.ALLOWED_UPLOAD_SIZE:
            return Response({'status': 'Bad request',
                             'message': 'You can only upload files with size less than' + str(
                                 settings.ALLOWED_UPLOAD_SIZE) + "kb."},
                            status=status.HTTP_400_BAD_REQUEST)

        if not agent.locations:
            load = []
        else:
            load = json.loads(agent.locations)

        path = default_storage.save('competition_files/agents/' + agent.agent_name + '/' + file_obj.name,
                                    ContentFile(file_obj.read()))

        load += [path]
        agent.locations = json.dumps(load)
        agent.save()

        return Response({'status': 'File uploaded!',
                         'message': 'The agent code has been uploaded!'},
                        status=status.HTTP_201_CREATED)


class UploadRoundXMLView(views.APIView):
    parser_classes = (FileUploadParser,)

    def __init__(self, file_to_save, folder):
        views.APIView.__init__(self)
        self.file_to_save = file_to_save
        self.folder = folder

    def get_permissions(self):
        return permissions.IsAuthenticated(), IsAdmin(),

    def post(self, request):
        if 'round' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?round=*round_name*'},
                            status=status.HTTP_400_BAD_REQUEST)

        r = get_object_or_404(Round.objects.all(), name=request.GET.get('round', ''))

        return self.file_save_xml(request.data['file'], r, )

    def file_save_xml(self, file_obj, r):
        if getattr(r, self.file_to_save, None) is not None:
            getattr(r, self.file_to_save, None).delete(False)

        if file_obj.size > 102400:
            return Response({'status': 'Bad request',
                             'message': 'You can only upload files with size less than 100KB.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if file_obj.content_type != 'application/xml':
            return Response({'status': 'Bad request',
                             'message': 'You can only upload XML files.'},
                            status=status.HTTP_400_BAD_REQUEST)

        path = default_storage.save('competition_files/' + self.folder + '/' + file_obj.name,
                                    ContentFile(file_obj.read()))

        setattr(r, self.file_to_save, path)
        r.save()

        return Response({'status': 'Uploaded',
                         'message': 'The file has been uploaded and saved to ' + str(r.name)},
                        status=status.HTTP_201_CREATED)


class UploadParamListView(UploadRoundXMLView):
    def __init__(self):
        UploadRoundXMLView.__init__(self, "param_list_path", "param_list")


class UploadGridView(UploadRoundXMLView):
    def __init__(self):
        UploadRoundXMLView.__init__(self, "grid_path", "grid")


class UploadLabView(UploadRoundXMLView):
    def __init__(self):
        UploadRoundXMLView.__init__(self, "lab_path", "lab")


"""
---------------------------------------------------------------
APAGAR A PARTE DA SIMULATION QUANDO AS RONDAS ESTIVEREM PRONTAS
---------------------------------------------------------------
"""


class GetSimulation(mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = SimulationSerializer

    def get_queryset(self):
        return [Simulation.objects.first()]

    @api_view(['GET'])
    def get_simulation(self, request):
        """
        B{Retrieve}: the first simulation
        B{URL:} ../api/v1/get_simulation/
        """

        serializer = self.serializer_class()
        return Response(serializer.data)


