from django.shortcuts import get_object_or_404
from os.path import basename, getsize, getmtime
from django.core.files.storage import default_storage
from django.db import IntegrityError
from django.db import transaction
from hurry.filesize import size

from rest_framework import permissions
from rest_framework import mixins, viewsets, status, views
from rest_framework.response import Response

from teams.serializers import TeamSerializer

from ..models import Competition, Round, CompetitionAgent
from ..serializers import RoundSerializer, RoundFilesSerializer, RFileSerializer, \
    FolderSerializer
from ..permissions import IsStaff, NotPrivateCompetition
from .simplex import RoundSimplex, RFile, FolderSimplex


class RoundViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                   mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Round.objects.all()
    serializer_class = RoundSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),
        return permissions.IsAuthenticated(), IsStaff(),

    def create(self, request, **kwargs):
        """
        B{Create} a Round
        B{URL:} ../api/v1/competitions/round/

        :type  name: str
        :param name: The round name
        :type  parent_competition_name: str
        :param parent_competition_name: The competition parent name
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
                                 'message': 'There is already a Round with that name in this competition!'},
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
        B{URL:} ../api/v1/competitions/round/<round_name>/?competition_name=<competition_name>

        :type  round_name: str
        :param round_name: The round name
        :type  competition_name: str
        :param competition_name: The competition name
        """
        if 'competition_name' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?competition_name=<competition_name>'},
                            status=status.HTTP_400_BAD_REQUEST)

        competition = get_object_or_404(Competition.objects.all(), name=request.GET.get('competition_name', ''))

        NotPrivateCompetition(competition=competition, message='This grid can\'t be seen!')

        r = get_object_or_404(self.queryset, name=kwargs.get('pk'), parent_competition=competition)
        serializer = self.serializer_class(RoundSimplex(r))
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        B{Remove} a round from the competition
        B{URL:} ../api/v1/competitions/round/<name>/?competition_name=<competition_name>

        :type  name: str
        :param name: The round name
        :type  competition_name: str
        :param competition_name: The competition name
        """
        if 'competition_name' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?competition_name=<competition_name>'},
                            status=status.HTTP_400_BAD_REQUEST)

        competition = get_object_or_404(Competition.objects.all(), name=request.GET.get('competition_name', ''))

        NotPrivateCompetition(competition=competition, message='This grid can\'t be seen!')

        r = get_object_or_404(self.queryset, name=kwargs.get('pk'), parent_competition=competition)
        r.delete()
        return Response(status=status.HTTP_200_OK)


class RoundTeams(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = CompetitionAgent.objects.all()
    serializer_class = TeamSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the teams available to compete in the round
        B{URL:} ../api/v1/competitions/round_teams/<round_name>/?competition_name=<competition_name>

        :type  round_name: str
        :param round_name: The round name
        :type  competition_name: str
        :param competition_name: The competition name
        """
        competition = get_object_or_404(Competition.objects.all(), name=request.GET.get('competition_name', ''))

        NotPrivateCompetition(competition=competition, message='This grid can\'t be seen!')

        r = get_object_or_404(Round.objects.all(), name=kwargs.get('pk'), parent_competition=competition)
        competition_agents = CompetitionAgent.objects.filter(round=r)
        competition_teams = [agent.agent.team for agent in competition_agents]
        serializer = self.serializer_class(competition_teams, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RoundFile(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Round.objects.all()
    serializer_class = RoundFilesSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated()

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the files uploaded to the round
        B{URL:} ../api/v1/competitions/round_files/<round_name>/?competition_name=<competition_name>

        :type  round_name: str
        :param round_name: The round name
        :type  competition_name: str
        :param competition_name: The competition name
        """
        competition = get_object_or_404(Competition.objects.all(), name=request.GET.get('competition_name', ''))
        r = get_object_or_404(self.queryset, name=kwargs.get('pk'), parent_competition=competition)

        class RsFile:
            def __init__(self, f):
                if not bool(f) or not default_storage.exists(f):
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
                self.param_list = RsFile(ro.param_list_path)
                self.grid = RsFile(ro.grid_path)
                self.lab = RsFile(ro.lab_path)

        serializer = self.serializer_class(RoundFiles(r))

        return Response(serializer.data, status=status.HTTP_200_OK)


class GetResourcesFiles(views.APIView):
    serializer_file_class = RFileSerializer
    serializer_folder_class = FolderSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def get(self, request):
        """
        B{Get} old and default params
        B{URL:} ../api/v1/round_resources/
        """
        serializer_lab = self.serializer_folder_class(self.recursive_names(dir_to_find='resources/labs'), many=True)
        serializer_grid = self.serializer_folder_class(self.recursive_names(dir_to_find='resources/grids'), many=True)
        serializer_param_list = self.serializer_folder_class(self.recursive_names(dir_to_find='resources/param_lists'),
                                                             many=True)
        return Response({'labs': serializer_lab.data,
                         'grids': serializer_grid.data,
                         'pram_lists': serializer_param_list.data}, status=status.HTTP_200_OK)

    def recursive_names(self, dir_to_find='resources'):
        dirs = default_storage.listdir(dir_to_find)

        files = []
        folders = []

        for d in dirs[0]:
            folders += self.recursive_names(dir_to_find=dir_to_find + "/" + str(d))
        for f in dirs[1]:
            files += [RFile(dir_to_find + "/" + str(f), f)]

        if len(files) == 0:
            return folders

        serializer = self.serializer_file_class(files, many=True)

        return folders + [FolderSimplex(dir_to_find.split("/")[-1], serializer.data)]