from django.shortcuts import get_object_or_404
from os.path import basename, getsize, getmtime
from django.core.files.storage import default_storage
from django.db import IntegrityError
from django.db import transaction
from hurry.filesize import size

from rest_framework import permissions
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response

from authentication.models import GroupMember
from authentication.serializers import AccountSerializer

from groups.serializers import GroupSerializer

from ..models import Competition, Round, CompetitionAgent
from ..serializers import RoundSerializer, RoundAgentSerializer, AdminRoundSerializer, RoundFilesSerializer
from ..permissions import IsStaff
from .simplex import RoundSimplex, CompetitionAgentSimplex


class RoundViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin,
                   mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Round.objects.all()
    serializer_class = RoundSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),
        return permissions.IsAuthenticated(), IsStaff(),

    def list(self, request, **kwargs):
        """
        B{List} of rounds
        B{URL:} ../api/v1/competitions/round/
        """
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
            try:
                with transaction.atomic():
                    Round.objects.create(name=serializer.validated_data['name'], parent_competition=competition)
            except IntegrityError:
                return Response({'status': 'Bad request',
                                 'message': 'The group already enrolled.'},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response({'status': 'Created',
                             'message': 'The round has been created.'},
                            status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the round competition
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
        r.delete()
        return Response(status=status.HTTP_200_OK)


class RoundViewAdminSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Round.objects.all()
    serializer_class = AdminRoundSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(), IsStaff(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the round competition for the admin
        B{URL:} ../api/v1/competitions/round_admin/<round_name>/

        @type  round_name: str
        @param round_name: The round name
        """
        r = get_object_or_404(self.queryset, name=kwargs.get('pk'))
        serializer = self.serializer_class(RoundSimplex(r))
        return Response(serializer.data, status=status.HTTP_200_OK)


class AgentsRound(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = CompetitionAgent.objects.all()
    serializer_class = RoundAgentSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the agents available to compete in the round
        B{URL:} ../api/v1/competitions/round_agents/<round_name>/

        @type  round_name: str
        @param round_name: The round name
        """
        r = get_object_or_404(Round.objects.all(), name=kwargs.get('pk'))
        competition_agents = CompetitionAgent.objects.filter(round=r)
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
        B{URL:} ../api/v1/competitions/round_participants/<round_name>/

        @type  round_name: str
        @param round_name: The round name
        """
        r = get_object_or_404(Round.objects.all(), name=kwargs.get('pk'))
        competition_agents = CompetitionAgent.objects.filter(round=r)
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
        B{URL:} ../api/v1/competitions/round_groups/<round_name>/

        @type  round_name: str
        @param round_name: The round name
        """
        r = get_object_or_404(Round.objects.all(), name=kwargs.get('pk'))
        competition_agents = CompetitionAgent.objects.filter(round=r)
        competition_groups = [agent.agent.group for agent in competition_agents]
        serializer = self.serializer_class(competition_groups, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RoundFile(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Round.objects.all()
    serializer_class = RoundFilesSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the files uploaded to the round
        B{URL:} ../api/v1/competitions/round_files/<round_name>/

        @type  round_name: str
        @param round_name: The round name
        """
        r = get_object_or_404(Round.objects.all(), name=kwargs.get('pk'))

        class RFile:
            def __init__(self, f):
                if not f:
                    self.file = ''
                    self.last_modification = None
                    self.size = size(0)
                    self.url = ""
                else:
                    self.file = basename(default_storage.path(f))
                    self.last_modification = getmtime(default_storage.path(f))
                    self.size = size(getsize(default_storage.path(f)))
                    self.url = ""

        class RoundFiles:
            def __init__(self, ro):
                self.param_list = RFile(ro.param_list_path)
                self.grid = RFile(ro.grid_path)
                self.lab = RFile(ro.lab_path)

        serializer = self.serializer_class(RoundFiles(r))

        return Response(serializer.data, status=status.HTTP_200_OK)