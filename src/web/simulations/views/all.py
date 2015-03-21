from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper

import os

from rest_framework import mixins, viewsets, status, views
from rest_framework.response import Response

from ..simplex import SimulationX
from ..serializers import SimulationXSerializer, LogSimulation
from ..models import Simulation

from competition.shortcuts import *


class SaveLogs(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Simulation.objects.all()
    serializer_class = LogSimulation

    """
    Must be discussed one simple way of authentication server to server
    """

    def create(self, request, *args, **kwargs):
        """
        B{Create} the json log
        B{URL:} ../api/v1/competitions/simulation_log/

        @type  log_json: str
        @param log_json: The json log
        @type  simulation_identifier: str
        @param simulation_identifier: The simulation identifier
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            simulation = Simulation.objects.get(identifier=serializer.validated_data['simulation_identifier'])

            if not simulation_started(simulation):
                return Response({'status': 'Bad Request',
                                 'message': 'The simulation should be stated first!'},
                                status=status.HTTP_400_BAD_REQUEST)

            simulation.log_json = serializer.validated_data['log_json']
            simulation.save()
            return Response({'status': 'Created',
                             'message': 'The log has been uploaded!'}, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': 'The simulation couldn\'t be updated with that data.'},
                        status=status.HTTP_400_BAD_REQUEST)


class GetSimulationLog(views.APIView):
    @staticmethod
    def get(request, simulation_id):
        """
        B{Get} simulation json log
        B{URL:} ../api/v1/competitions/get_simulation_log/<simulation_id>/

        @type  simulation_id: str
        @param simulation_id: The simulation identifier
        """
        simulation = get_object_or_404(Simulation.objects.all(), identifier=simulation_id)

        if not simulation_done(simulation):
            return Response({'status': 'Bad request',
                             'message': 'The simulation must have a log!'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            file = default_storage.open(simulation.log_json)
        except Exception:
            return Response({'status': 'Bad request',
                             'message': 'The file doesn\'t exists'},
                            status=status.HTTP_400_BAD_REQUEST)

        wrapper = FileWrapper(file)
        response = HttpResponse(wrapper, content_type="application/x-compressed")
        response['Content-Disposition'] = 'attachment; filename=' + simulation_id + '.tar.gz'
        response['Content-Length'] = os.path.getsize(file.name)
        file.seek(0)
        return response


class GetSimulation(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Simulation.objects.all()
    serializer_class = SimulationXSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the simulation complete, machine-to-machine
        B{URL:} ../api/v1/competitions/get_simulation/<simulation_id>/

        @type  simulation_id: str
        @param simulation_id: The simulation id
        """
        simulation = get_object_or_404(self.queryset, identifier=kwargs.get('pk'))
        serializer = self.serializer_class(SimulationX(simulation))
        simulation.started = True
        simulation.save()

        return Response(serializer.data, status=status.HTTP_200_OK)