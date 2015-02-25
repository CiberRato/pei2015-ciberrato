from competition.models import Simulation
from competition.serializers import SimulationSerializer

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response


class GetSimulation(mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = SimulationSerializer

    def get_queryset(self):
        return [Simulation.objects.first()]

    # missing change the attribute sent = True
    @api_view(['GET'])
    def get_simulation(self, request):
        """
        B{Retrieve}: the first simulation
        B{URL:} ../api/v1/get_simulation/
        """
        queryset = self.get_queryset()
        print >> sys.stderr, request.build_absolute_url()

        if not queryset:
            return Response({'status': 'Without simulation',
                             'message': 'Does not exist simulations in the system.'},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(queryset[0])
        return Response(serializer.data)