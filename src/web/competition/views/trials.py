from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.conf import settings
from django.db import IntegrityError, transaction

import bz2

from rest_framework import mixins, viewsets, status, views
from rest_framework.response import Response
from rest_framework import permissions

from .simplex import TrialX
from ..serializers import TrialXSerializer, LogTrial, ErrorTrial, TrialMessageSerializer
from ..models import Trial, TeamEnrolled, PrivateCompetitionLog, LogTrialAgent
from ..renderers import JSONRenderer

from competition.shortcuts import *
from notifications.models import NotificationBroadcast, NotificationTeam


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
            trial = get_object_or_404(Trial.objects.all(), identifier=serializer.validated_data['trial_identifier'])

            if not trial_started(trial):
                return Response({'status': 'Bad Request',
                                 'message': 'The trial should be started first!'},
                                status=status.HTTP_400_BAD_REQUEST)

            serializer.validated_data['log_json'].name = trial.identifier + '.json.bz2'
            trial.log_json = serializer.validated_data['log_json']
            trial.save()

            # if is a private competition
            if trial.round.parent_competition.type_of_competition.name == settings.PRIVATE_COMPETITIONS_NAME:
                try:
                    with transaction.atomic():
                        # get team
                        team = TeamEnrolled.objects.filter(competition=trial.round.parent_competition).first().team

                        # search logs
                        logs = PrivateCompetitionLog.objects.order_by('created_at').filter(team=team)

                        # save log reference
                        PrivateCompetitionLog.objects.create(team=team, trial=trial)

                        # clean logs
                        if len(logs) > settings.MAX_PRIVATE_COMPETITION_LOGS_SAVED_PER_TEAM:
                            for log in logs[0:len(logs) - settings.MAX_PRIVATE_COMPETITION_LOGS_SAVED_PER_TEAM]:
                                try:
                                    trial_log = log.trial
                                    log.delete()
                                    trial_log.delete()
                                except Trial.DoesNotExist:
                                    pass
                except IntegrityError:
                    pass

            if trial.round.parent_competition.type_of_competition.name == settings.PRIVATE_COMPETITIONS_NAME or \
                    trial.round.parent_competition.type_of_competition.name == settings.HALL_OF_FAME_START_STR + 'Single':
                t = LogTrialAgent.objects.filter(trial=trial)
                team = t.first()
                team = team.competition_agent.agent.team

                NotificationTeam.add(team=team, status="ok",
                                     message="The trial of " + trial.round.name + " has finished!",
                                     trigger="trial_log")
            else:
                NotificationBroadcast.add(channel="user", status="ok",
                                          message="The trial of " + trial.round.name + " has finished!",
                                          trigger="trial_log")

            return Response({'status': 'Created',
                             'message': 'The log has been uploaded!'}, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class TrialMessageCreate(views.APIView):
    serializer_class = TrialMessageSerializer

    def post(self, request):
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
            try:
                trial = Trial.objects.get(identifier=serializer.validated_data['trial_identifier'])
            except Trial.DoesNotExist:
                return Response({'status': 'Bad request',
                                'message': 'The trial message can\'t be saved!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if trial_done(trial):
                return Response({'status': 'Bad request',
                                 'message': 'The trial message can\'t be saved, the Trial is in LOG state!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if trial.round.parent_competition.type_of_competition.name == settings.PRIVATE_COMPETITIONS_NAME or \
                            trial.round.parent_competition.type_of_competition.name == settings.HALL_OF_FAME_START_STR + 'Single':
                t = LogTrialAgent.objects.filter(trial=trial)
                team = t.first()
                team = team.competition_agent.agent.team

                NotificationTeam.add(team=team, status="ok",
                                     message=serializer.validated_data['message'])
            else:
                NotificationBroadcast.add(channel="admin", status="info",
                                          message=serializer.validated_data['message'])

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
            trial = get_object_or_404(Trial.objects.all(), identifier=serializer.validated_data['trial_identifier'])

            trial.errors = serializer.validated_data['msg']
            trial.save()

            if trial.round.parent_competition.type_of_competition.name == settings.PRIVATE_COMPETITIONS_NAME or \
                            trial.round.parent_competition.type_of_competition.name == settings.HALL_OF_FAME_START_STR + 'Single':
                try:
                    t = LogTrialAgent.objects.filter(trial=trial)
                    team = t.first()
                    team = team.competition_agent.agent.team

                    NotificationTeam.add(team=team, status="error",
                                         message="The trial of " + trial.round.name + " has encountered an error!",
                                         trigger="trial_error")
                except AttributeError:
                    Response({'status': 'Bad Request',
                              'message': 'There are no agents!'},
                             status=status.HTTP_400_BAD_REQUEST)
            else:
                NotificationBroadcast.add(channel="admin", status="error",
                                          message="The trial of " + trial.round.name + " has encountered an error!",
                                          trigger="trial_error")

            return Response({'status': 'Created',
                             'message': 'The msg error has been saved!'}, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class GetTrialLog(views.APIView):
    renderer_classes = (JSONRenderer, )

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    @staticmethod
    def get(request, trial_id):
        """
        B{Get} trial json log
        B{URL:} ../api/v1/trials/get_trial_log/<trial_id>/

        :type  trial_id: str
        :param trial_id: The trial identifier
        """
        trial = get_object_or_404(Trial.objects.all(), identifier=trial_id)

        # can not be private competition
        if trial.round.parent_competition.type_of_competition.name == settings.PRIVATE_COMPETITIONS_NAME:
            if trial.round.parent_competition.teamenrolled_set.first().team not in request.user.teams.all():
                return Response({'status': 'Bad request',
                                 'message': 'You can not see the rounds for this competition!'},
                                status=status.HTTP_400_BAD_REQUEST)

        if not trial_done(trial):
            return Response({'status': 'Bad request',
                             'message': 'The trial must have a log!'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            json_text = bz2.decompress(default_storage.open(trial.log_json).read())
        except Exception:
            return Response({'status': 'Bad request',
                             'message': 'The file doesn\'t exists'},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(json_text)


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

        if trial.round.parent_competition.type_of_competition.allow_remote_agents is False:
            trial.waiting = False
            trial.prepare = False
            trial.started = True

            if trial.round.parent_competition.type_of_competition.name == settings.PRIVATE_COMPETITIONS_NAME or \
                trial.round.parent_competition.type_of_competition.name == settings.HALL_OF_FAME_START_STR + 'Single':
                    try:
                        team = trial.logtrialagent_set.first()
                        team = team.competition_agent.agent.team
                    except Exception:
                        return Response({'status': 'Bad request',
                                         'message': 'The trial must have one agent!'},
                                        status=status.HTTP_400_BAD_REQUEST)

                    NotificationTeam.add(team=team, status="ok",
                                         message="The trial has started!",
                                         trigger="trial_started")
            else:
                NotificationBroadcast.add(channel="user", status="ok",
                                          message="The trial of " + trial.round.name + " has started!",
                                          trigger="trial_start")
        else:
            trial.waiting = False
            trial.prepare = True
            trial.started = False
            NotificationBroadcast.add(channel="user", status="ok",
                                      message="The trial of " + trial.round.name + " can now be started!",
                                      trigger="trial_prepare")
        trial.save()

        return Response(serializer.data, status=status.HTTP_200_OK)