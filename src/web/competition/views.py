from django.shortcuts import get_object_or_404
from competition.models import Competition, Simulation
from competition.serializers import CompetitionSerializer, SimulationSerializer

from rest_framework import permissions
from rest_framework import mixins, viewsets, views, status

from rest_framework.decorators import api_view
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from competition.permissions import IsAdmin


class CompetitionViewSet(viewsets.ModelViewSet):
    queryset = Competition.objects.order_by('-name')
    serializer_class = CompetitionSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),

        if self.request.method == 'POST':
            return permissions.IsAuthenticated(),

        return permissions.IsAuthenticated, IsAdmin(),

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

        competition.delete()

        return Response({'status': 'Deleted',
                         'message': 'The competition has been deleted'},
                        status=status.HTTP_200_OK)


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


class FileUploadView(views.APIView):
    # parser_classes = (FormParser, MultiPartParser,FileUploadParser,)
    parser_classes = (FileUploadParser,)

    def post(self, request, format=None):
        print type(request)
        print request.data
        file_obj = request.data['file']
        # <class 'django.core.files.uploadedfile.InMemoryUploadedFile'>
        filename = file_obj.name
        path = default_storage.save('competition_files/grids/' + filename, ContentFile(file_obj.read()))
        # DANGER, IF FILE IS TOO BIG

        return Response({'status': 'Uploaded',
                         'message': 'The file has been uploaded.'},
                        status=status.HTTP_200_OK)
