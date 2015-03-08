from django.shortcuts import get_object_or_404
from competition.models import Competition, Round, CompetitionAgent
from competition.serializers import RoundSerializer, CompetitionAgentSerializer
from authentication.models import GroupMember
from authentication.serializers import AccountSerializer
from groups.serializers import GroupSerializer
from rest_framework import permissions
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from competition.permissions import IsAdmin
from competition.views.simplex import RoundSimplex, CompetitionAgentSimplex


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

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the oldest round competition
        B{URL:} ../api/v1/competitions/round/<round_name>/

        @type  round_name: str
        @param round_name: The round name
        """
        r = get_object_or_404(self.queryset, name=kwargs.get('pk'))

        serializer = self.serializer_class(RoundSimplex(r))

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        B{Remove} a round from the competition
        B{URL:} ../api/v1/competitions/round/<name>/

        @type  name: str
        @param name: The round name
        """
        r = get_object_or_404(self.queryset, name=kwargs.get('pk'))

        for c_agent in CompetitionAgent.objects.all():
            c_agent.delete()

        r.delete()

        return Response(status=status.HTTP_200_OK)


class AgentsRound(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = CompetitionAgent.objects.all()
    serializer_class = CompetitionAgentSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the agents available to compete in the round
        B{URL:} ../api/v1/competitions/valid_round_agents/<round_name>/

        @type  round_name: str
        @param round_name: The round name
        """
        r = get_object_or_404(Round.objects.all(), name=kwargs.get('pk'))
        competition_agents = CompetitionAgent.objects.filter(round=r, eligible=True)
        competition_agents = [CompetitionAgentSimplex(agent) for agent in competition_agents]
        serializer = self.serializer_class(competition_agents, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class AgentsNotEligible(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = CompetitionAgent.objects.all()
    serializer_class = CompetitionAgentSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the agents available to compete in the round
        B{URL:} ../api/v1/competitions/not_eligible_round_agents/<round_name>/

        @type  round_name: str
        @param round_name: The round name
        """
        r = get_object_or_404(Round.objects.all(), name=kwargs.get('pk'))
        competition_agents = CompetitionAgent.objects.filter(round=r, eligible=False)
        competition_agents = [CompetitionAgentSimplex(agent) for agent in competition_agents]
        serializer = self.serializer_class(competition_agents, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RoundParticipants(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = CompetitionAgent.objects.all()
    serializer_class = AccountSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the participants available to compete in the round
        B{URL:} ../api/v1/competitions/valid_round_participants/<round_name>/

        @type  round_name: str
        @param round_name: The round name
        """
        r = get_object_or_404(Round.objects.all(), name=kwargs.get('pk'))
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

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the participants available to compete in the round
        B{URL:} ../api/v1/competitions/not_eligible_round_participants/<round_name>/

        @type  round_name: str
        @param round_name: The round name
        """
        r = get_object_or_404(Round.objects.all(), name=kwargs.get('pk'))
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

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the groups available to compete in the round
        B{URL:} ../api/v1/competitions/valid_round_groups/<round_name>/

        @type  round_name: str
        @param round_name: The round name
        """
        r = get_object_or_404(Round.objects.all(), name=kwargs.get('pk'))
        competition_agents = CompetitionAgent.objects.filter(round=r, eligible=True)
        competition_groups = [agent.agent.group for agent in competition_agents]
        serializer = self.serializer_class(competition_groups, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RoundGroupsNotEligible(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = CompetitionAgent.objects.all()
    serializer_class = GroupSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the groups available to compete in the round
        B{URL:} ../api/v1/competitions/not_eligible_round_groups/<round_name>/

        @type  round_name: str
        @param round_name: The round name
        """
        r = get_object_or_404(Round.objects.all(), name=kwargs.get('pk'))
        competition_agents = CompetitionAgent.objects.filter(round=r, eligible=False)
        competition_groups = [agent.agent.group for agent in competition_agents]
        serializer = self.serializer_class(competition_groups, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
