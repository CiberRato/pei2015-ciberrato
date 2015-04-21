from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper

import os

from rest_framework import mixins, viewsets, status, views
from rest_framework.response import Response

from ..simplex import TrialX
from ..serializers import TrialXSerializer, LogTrial, ErrorTrial
from ..models import Trial

from competition.shortcuts import *


class SaveLogs(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Trial.objects.all()
    serializer_class = LogTrial

    """
    Must be discussed one simple way of authentication server to server
    """

    def create(self, request, *args, **kwargs):
        """
        B{Create} the json log
        B{URL:} ../api/v1/trials/trial_log/

        @type  log_json: str
        @param log_json: The json log
        @type  trial_identifier: str
        @param trial_identifier: The trial identifier
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            trial = Trial.objects.get(identifier=serializer.validated_data['trial_identifier'])

            if not trial_started(trial):
                return Response({'status': 'Bad Request',
                                 'message': 'The trial should be stated first!'},
                                status=status.HTTP_400_BAD_REQUEST)

            trial.log_json = serializer.validated_data['log_json']
            trial.save()
            return Response({'status': 'Created',
                             'message': 'The log has been uploaded!'}, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class SaveSimErrors(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Trial.objects.all()
    serializer_class = ErrorTrial

    def create(self, request, *args, **kwargs):
        """
        B{Create} the trial error
        B{URL:} ../api/v1/trials/trial_error/

        @type  msg: str
        @param msg: The error
        @type  trial_identifier: str
        @param trial_identifier: The trial identifier
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            trial = Trial.objects.get(identifier=serializer.validated_data['trial_identifier'])

            trial.errors = serializer.validated_data['msg']
            trial.save()

            return Response({'status': 'Created',
                             'message': 'The msg error has been uploaded!'}, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

class GetTrialLog(views.APIView):
    @staticmethod
    def get(request, trial_id):
        """
        B{Get} trial json log
        B{URL:} ../api/v1/trials/get_trial_log/<trial_id>/

        @type  trial_id: str
        @param trial_id: The trial identifier
        """
        trial = get_object_or_404(Trial.objects.all(), identifier=trial_id)

        if not trial_done(trial):
            return Response({'status': 'Bad request',
                             'message': 'The trial must have a log!'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            file = default_storage.open(trial.log_json)
        except Exception:
            return Response({'status': 'Bad request',
                             'message': 'The file doesn\'t exists'},
                            status=status.HTTP_400_BAD_REQUEST)

        wrapper = FileWrapper(file)
        response = HttpResponse(wrapper, content_type="application/x-compressed")
        response['Content-Disposition'] = 'attachment; filename=' + trial_id + '.tar.gz'
        response['Content-Length'] = os.path.getsize(file.name)
        file.seek(0)
        return response


class GetTrial(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Trial.objects.all()
    serializer_class = TrialXSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the trial complete, machine-to-machine
        B{URL:} ../api/v1/trials/get_trial/<trial_id>/

        @type  trial_id: str
        @param trial_id: The trial id
        """
        trial = get_object_or_404(self.queryset, identifier=kwargs.get('pk'))
        serializer = self.serializer_class(TrialX(trial))
        trial.started = True
        trial.save()

        return Response(serializer.data, status=status.HTTP_200_OK)