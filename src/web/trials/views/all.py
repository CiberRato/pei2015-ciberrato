from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from django.db import IntegrityError
from django.db import transaction

import os

from rest_framework import mixins, viewsets, status, views
from rest_framework.response import Response

from ..simplex import TrialX
from ..serializers import TrialXSerializer, LogTrial, ErrorTrial, TrialMessageSerializer
from ..models import Trial, TrialMessage

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

        :type  log_json: str
        :param log_json: The json log
        :type  trial_identifier: str
        :param trial_identifier: The trial identifier
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

            for trial_message in TrialMessage.objects.filter(trial=trial):
                trial_message.delete()

            return Response({'status': 'Created',
                             'message': 'The log has been uploaded!'}, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class TrialMessageCreate(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = TrialMessage.objects.all()
    serializer_class = TrialMessageSerializer

    def create(self, request, *args, **kwargs):
        """
        B{Create} the trial message
        B{URL:} ../api/v1/trials/message/

        :type  message: str
        :param message: The message
        :type  trial_identifier: str
        :param trial_identifier: The trial identifier
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            trial = Trial.objects.get(identifier=serializer.validated_data['trial_identifier'])

            if trial_done(trial):
                return Response({'status': 'Bad request',
                                 'message': 'The trial message can\'t be saved, the Trial is in LOG state!'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                with transaction.atomic():
                    TrialMessage.objects.create(trial=trial, message=serializer.validated_data['message'])
            except IntegrityError:
                return Response({'status': 'Bad request',
                                 'message': 'The trial message can\'t be saved!'},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response({'status': 'Created',
                             'message': 'The message has been saved!'}, status=status.HTTP_201_CREATED)

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

        :type  msg: str
        :param msg: The error
        :type  trial_identifier: str
        :param trial_identifier: The trial identifier
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            trial = Trial.objects.get(identifier=serializer.validated_data['trial_identifier'])

            trial.errors = serializer.validated_data['msg']
            trial.save()

            return Response({'status': 'Created',
                             'message': 'The msg error has been saved!'}, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class GetTrialLog(views.APIView):
    @staticmethod
    def get(request, trial_id):
        """
        B{Get} trial json log
        B{URL:} ../api/v1/trials/get_trial_log/<trial_id>/

        :type  trial_id: str
        :param trial_id: The trial identifier
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

        :type  trial_id: str
        :param trial_id: The trial id
        """
        trial = get_object_or_404(self.queryset, identifier=kwargs.get('pk'))
        serializer = self.serializer_class(TrialX(trial))

        trial.started = True
        trial.save()

        # NotificationUser.add(team=team, status="ok", message=account.username + " has logged in!")

        return Response(serializer.data, status=status.HTTP_200_OK)