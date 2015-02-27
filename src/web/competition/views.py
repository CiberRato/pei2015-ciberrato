from django.shortcuts import get_object_or_404

from competition.models import Competition, Simulation
from competition.serializers import CompetitionSerializer, SimulationSerializer

from rest_framework import mixins, viewsets, status, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response

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

            return Response(serializer.validated_data, status = status.HTTP_201_CREATED)

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


