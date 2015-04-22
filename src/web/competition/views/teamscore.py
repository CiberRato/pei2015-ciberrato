from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db import transaction

from rest_framework import permissions
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from authentication.models import Team

from .simplex import TeamScoreSimplex
from ..models import Competition, TeamScore, TeamEnrolled, Trial, Round
from ..serializers import TeamScoreOutSerializer, TeamScoreInSerializer
from ..permissions import IsStaff


class TeamScoreViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                       mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = TeamScore.objects.all()
    serializer_class = TeamScoreOutSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),
        return permissions.IsAuthenticated(), IsStaff(),

    def list(self, request, *args, **kwargs):
        """
        B{List} user teams scores
        B{URL:} ../api/v1/competitions/team_score/
        """
        team_score_list = []

        for group in request.user.groups.all():
            team_score_list += group.teamscore_set.all()

        serializer = self.serializer_class([TeamScoreSimplex(team_score) for team_score in team_score_list], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        B{Create} a team score
        B{URL:} ../api/v1/competitions/team_score/

        @type  trial_id: str
        @param trial_id: The trial identifier
        @type  team_name: str
        @param team_name: The team name
        @type  score: Integer
        @param score: The score
        @type  number_of_agents: Integer
        @param number_of_agents: The number of agents
        @type  time: Integer
        @param time: The time
        """
        serializer = TeamScoreInSerializer(data=request.data)

        if serializer.is_valid():
            trial = get_object_or_404(Trial.objects.all(), identifier=serializer.validated_data['trial_id'])

            if trial.round.parent_competition.state_of_competition == 'Past':
                return Response({'status': 'Bad Request',
                                 'message': 'The competition is in \'Past\' state.'},
                                status=status.HTTP_400_BAD_REQUEST)

            team = get_object_or_404(Team.objects.all(), name=serializer.validated_data['team_name'])

            group_enrolled = TeamEnrolled.objects.filter(group=team, competition=trial.round.parent_competition)

            if len(group_enrolled) != 1:
                return Response({'status': 'Permission denied',
                                 'message': 'The team must be enrolled in the competition.'},
                                status=status.HTTP_403_FORBIDDEN)

            if not group_enrolled[0].valid:
                return Response({'status': 'Permission denied',
                                 'message': 'The team must be enrolled in the competition with valid inscription.'},
                                status=status.HTTP_403_FORBIDDEN)

            try:
                with transaction.atomic():
                    team_score = TeamScore.objects.create(trial=trial, team=team,
                                                          score=serializer.validated_data['score'],
                                                          number_of_agents=serializer.validated_data[
                                                              'number_of_agents'],
                                                          time=serializer.validated_data['time'])
                    serializer = self.serializer_class(TeamScoreSimplex(team_score))
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({'status': 'Bad request',
                                 'message': 'There is already a score for that team in the trial!'},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        B{Update} a team score
        B{URL:} ../api/v1/competitions/team_score/<trial_id>/

        @type  trial_id: str
        @param trial_id: The trial identifier
        @type  team_name: str
        @param team_name: The team name
        @type  score: Integer
        @param score: The score
        @type  number_of_agents: Integer
        @param number_of_agents: The number of agents
        @type  time: Integer
        @param time: The time
        """
        serializer = TeamScoreInSerializer(data=request.data)

        if serializer.is_valid():
            trial = get_object_or_404(Trial.objects.all(), identifier=serializer.validated_data['trial_id'])

            if trial.round.parent_competition.state_of_competition == 'Past':
                return Response({'status': 'Bad Request',
                                 'message': 'The competition is in \'Past\' state.'},
                                status=status.HTTP_400_BAD_REQUEST)

            team = get_object_or_404(Team.objects.all(), name=serializer.validated_data['team_name'])

            group_enrolled = TeamEnrolled.objects.filter(group=team, competition=trial.round.parent_competition)

            if len(group_enrolled) != 1:
                return Response({'status': 'Permission denied',
                                 'message': 'The team must be enrolled in the competition.'},
                                status=status.HTTP_403_FORBIDDEN)

            if not group_enrolled[0].valid:
                return Response({'status': 'Permission denied',
                                 'message': 'The team must be enrolled in the competition with valid inscription.'},
                                status=status.HTTP_403_FORBIDDEN)

            team_score = get_object_or_404(TeamScore.objects.all(), trial=trial, team=team)

            try:
                with transaction.atomic():
                    team_score.score = serializer.validated_data['score']
                    team_score.number_of_agents = serializer.validated_data['number_of_agents']
                    team_score.time = serializer.validated_data['time']
                    team_score.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
            except IntegrityError:
                return Response({'status': 'Bad request',
                                 'message': 'The team score can\'t be updated!'},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} the team score
        B{URL:} ../api/v1/competitions/team_score/<trial_id>/?team_name=<team_name>

        @type  trial_id: str
        @param trial_id: The trial identifier
        @type  team_name: str
        @type  team_name: The team name
        """
        trial = get_object_or_404(Trial.objects.all(), identifier=kwargs.get('pk', ''))

        if trial.round.parent_competition.state_of_competition == 'Past':
            return Response({'status': 'Bad Request',
                             'message': 'The competition is in \'Past\' state.'},
                            status=status.HTTP_400_BAD_REQUEST)

        team = get_object_or_404(Team.objects.all(), name=request.GET.get('team_name', ''))

        team_score = get_object_or_404(TeamScore.objects.all(), trial=trial, team=team)
        team_score.delete()

        return Response({'status': 'Deleted',
                         'message': 'The team score has been deleted!'},
                        status=status.HTTP_200_OK)


class RankingByTrial(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = TeamScore.objects.all()
    serializer_class = TeamScoreOutSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the ranking for the trial
        B{URL:} ../api/v1/competitions/ranking_trial/<trial_id>/

        @type  trial_id: str
        @param trial_id: The trial id
        """
        trial = get_object_or_404(Trial.objects.all(), identifier=kwargs.get('pk'))
        serializer = self.serializer_class([TeamScoreSimplex(team_score) for team_score in trial.teamscore_set.all()],
                                           many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RankingByRound(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = TeamScore.objects.all()
    serializer_class = TeamScoreOutSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the ranking for the round
        B{URL:} ../api/v1/competitions/ranking_round/<round_name>/

        @type  round_name: str
        @param round_name: The round name
        """
        r = get_object_or_404(Round.objects.all(), name=kwargs.get('pk'))

        trials = []
        for trial in r.trial_set.all():
            trials += trial.teamscore_set.all()

        serializer = self.serializer_class([TeamScoreSimplex(team_score) for team_score in trials], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RankingByCompetition(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = TeamScore.objects.all()
    serializer_class = TeamScoreOutSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the ranking for the competition
        B{URL:} ../api/v1/competitions/ranking_competition/<competition_name>/

        @type  competition_name: str
        @param competition_name: The competition name
        """
        competition = get_object_or_404(Competition.objects.all(), name=kwargs.get('pk'))

        trials = []

        for r in competition.round_set.all():
            for trial in r.trial_set.all():
                trials += trial.teamscore_set.all()

        serializer = self.serializer_class([TeamScoreSimplex(team_score) for team_score in trials], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)