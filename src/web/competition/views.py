from django.shortcuts import get_object_or_404
from competition.models import Competition, Round, Simulation, GroupEnrolled, CompetitionAgent
from competition.serializers import CompetitionSerializer, RoundSerializer, SimulationSerializer, \
    GroupEnrolledSerializer
from django.db import IntegrityError
from django.db import transaction
from authentication.models import Group

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
                             'message': 'You can only upload photos with size less than 100KB.'},
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


