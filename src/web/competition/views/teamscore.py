from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db import transaction

from rest_framework import permissions
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from authentication.models import Group, GroupMember

from .simplex import GridPositionsSimplex, AgentGridSimplex, TeamScoreSimplex
from ..models import Competition, TeamScore, GroupEnrolled, AgentGrid, Agent, Simulation
from ..serializers import GridPositionsSerializer, AgentGridSerializer, TeamScoreOutSerializer, TeamScoreInSerializer
from ..permissions import IsStaff


class TeamScoreViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                       mixins.RetrieveModelMixin, viewsets.GenericViewSet):
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
        @type  team_name: The team name
        """
        serializer = TeamScoreInSerializer(data=request.data)

        if serializer.is_valid():
            trial = get_object_or_404(Simulation.objects.all(), identifier=serializer.validated_data['trial_id'])

            if trial.round.parent_competition.state_of_competition == 'Past':
                return Response({'status': 'Bad Request',
                                 'message': 'The competition is in \'Past\' state.'},
                                status=status.HTTP_400_BAD_REQUEST)

            team = get_object_or_404(Group.objects.all(), name=serializer.validated_data['team_name'])

            group_enrolled = GroupEnrolled.objects.filter(group=team, competition=trial.round.parent_competition)

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

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the grid positions details
        B{URL:} ../api/v1/competitions/grid_positions/<competition_name>/?group_name=<group_name>

        @type  competition_name: str
        @param competition_name: The type of competition name
        @type  group_name: str
        @type  group_name: The group name
        """
        serializer = self.serializer_class(GridPositionsSimplex(grid))

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} the grid positions
        B{URL:} ../api/v1/competitions/grid_positions/<competition_name>/?group_name=<group_name>

        @type  competition_name: str
        @param competition_name: The type of competition name
        @type  group_name: str
        @type  group_name: The group name
        """
        return Response({'status': 'Deleted',
                         'message': 'The grid positions has been deleted'},
                        status=status.HTTP_200_OK)