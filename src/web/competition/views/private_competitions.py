from django.shortcuts import get_object_or_404
from django.db import IntegrityError
import uuid
from django.db import transaction
from django.conf import settings
from django.core.files.storage import default_storage

from rest_framework import permissions
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from authentication.models import Team, TeamMember

from .simplex import GridPositionsSimplex, AgentGridSimplex
from ..models import Competition, GridPositions, TeamEnrolled, AgentGrid, Agent, TrialGrid, Round, Trial
from ..serializers import CompetitionSerializer, PrivateCompetitionSerializer, PrivateRoundSerializer, \
    InputPrivateRoundSerializer, TrialSerializer, PrivateRoundTrialsSerializer
from .simplex import TrialSimplex
from ..permissions import IsStaff
from authentication.models import Account


class PrivateCompetitionsUser(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = PrivateCompetitionSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def list(self, request, *args, **kwargs):
        """
        B{List} user private competitions
        B{URL:} ../api/v1/competitions/private/list/
        """
        private_competitions_team_enrolled = []

        for team in request.user.teams.all():
            for team_enrolled in team.teamenrolled_set.all():
                if team_enrolled.competition.type_of_competition.name == settings.PRIVATE_COMPETITIONS_NAME:
                    private_competitions_team_enrolled += [team_enrolled]

        serializer = self.serializer_class(private_competitions_team_enrolled, many=True)

        return Response(serializer.data)


class PrivateCompetitionsRounds(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = PrivateRoundSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{List} private competition rounds
        B{URL:} ../api/v1/competitions/private/rounds/<competition_name>/
        """
        private_competition = Competition.objects.get(name=kwargs.get('pk'))

        # this competition must be a private competition
        if private_competition.type_of_competition.name != settings.PRIVATE_COMPETITIONS_NAME:
            return Response({'status': 'Bad request',
                             'message': 'You can only see this for private competitions!'},
                            status=status.HTTP_400_BAD_REQUEST)

        # verify if the team is enrolled in the competition
        team_enrolled = TeamEnrolled.objects.filter(competition=private_competition).first()
        if team_enrolled.team not in request.user.teams.all():
            return Response({'status': 'Bad request',
                             'message': 'You can not see the rounds for this competition!'},
                            status=status.HTTP_400_BAD_REQUEST)

        # get round for this competition
        rounds = Round.objects.filter(parent_competition=private_competition)
        serializer = self.serializer_class(rounds, many=True)

        return Response(serializer.data)


class CreatePrivateCompetitionRound(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = InputPrivateRoundSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def create(self, request, *args, **kwargs):
        """
        B{Create} a private competition round
        B{URL:} ../api/v1/competitions/private/create_round/

        :type  competition_name: str
        :param competition_name: The competition name
        :type  grid: str
        :param grid: The grid path from resources
        :type  param_list: str
        :param param_list: The param_list from resources
        :type  lab: str
        :param lab: The lab from resources
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            private_competition = get_object_or_404(Competition.objects.all(),
                                                    name=serializer.validated_data['competition_name'])

            # this competition must be a private competition
            if private_competition.type_of_competition.name != settings.PRIVATE_COMPETITIONS_NAME:
                return Response({'status': 'Bad request',
                                 'message': 'You can only see this for private competitions!'},
                                status=status.HTTP_400_BAD_REQUEST)

            # verify if the team is enrolled in the competition
            team_enrolled = TeamEnrolled.objects.filter(competition=private_competition).first()
            if team_enrolled.team not in request.user.teams.all():
                return Response({'status': 'Bad request',
                                 'message': 'You can not see the rounds for this competition!'},
                                status=status.HTTP_400_BAD_REQUEST)

            # create a round for this competition
            try:
                with transaction.atomic():
                    r = Round.objects.create(name=uuid.uuid4(), parent_competition=private_competition)
                    CreatePrivateCompetitionRound.set_param(r, serializer.validated_data['grid'], 'grid')
                    CreatePrivateCompetitionRound.set_param(r, serializer.validated_data['param_list'], 'param_list')
                    CreatePrivateCompetitionRound.set_param(r, serializer.validated_data['lab'], 'lab')
            except IntegrityError, e:
                return Response({'status': 'Bad request',
                                 'message': e.message},
                                status=status.HTTP_400_BAD_REQUEST)

            serializer = PrivateRoundSerializer(r)
            return Response(serializer.data)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def set_param(r, path, param):
        if not default_storage.exists(path):
            raise IntegrityError('The file doesn\'t exists!')

        # verify if is a valid path
        if not path.startswith('resources/'):
            raise IntegrityError('Invalid file!')

        setattr(r, param + "_path", default_storage.path(path))
        setattr(r, param + "_can_delete", False)
        r.save()


class GetRoundTrials(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Round.objects.all()
    serializer_class = PrivateRoundTrialsSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        B{List} the trials for one round and the file list
        B{URL:} ../api/v1/competitions/private/round/<round_name>/
        """
        # the round must exist
        r = Round.objects.get(name=kwargs.get('pk'))

        # the parent competition of the round must be private competition
        if r.parent_competition.type_of_competition.name != settings.PRIVATE_COMPETITIONS_NAME:
            return Response({'status': 'Bad request',
                             'message': 'You can only see this for private competitions!'},
                            status=status.HTTP_400_BAD_REQUEST)

        # the team must be enrolled in the parent competition
        team_enrolled = TeamEnrolled.objects.filter(competition=r.parent_competition).first()
        if team_enrolled.team not in request.user.teams.all():
            return Response({'status': 'Bad request',
                             'message': 'You can not see the rounds for this competition!'},
                            status=status.HTTP_400_BAD_REQUEST)

        # get the trials
        trials = Trial.objects.filter(round=r)
        trials = [TrialSimplex(trial) for trial in trials]

        class PrivateRoundTrials:
            def __init__(self, rnd, trials_simplex):
                serializer = PrivateRoundSerializer(rnd)
                self.round = serializer.data
                serializer = TrialSerializer(trials_simplex, many=True)
                self.trials = serializer.data

        # join the trials with the files name
        private_round = PrivateRoundTrials(r, trials)

        # serializer
        serializer = self.serializer_class(private_round)

        return Response(serializer.data)