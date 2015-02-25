from competition.models import Simulation
from competition.serializers import SimulationSerializer

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response


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


