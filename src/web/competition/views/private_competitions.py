from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db import transaction
from django.conf import settings

from rest_framework import permissions
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from authentication.models import Team, TeamMember

from .simplex import GridPositionsSimplex, AgentGridSimplex
from ..models import Competition, GridPositions, TeamEnrolled, AgentGrid, Agent, TrialGrid
from ..serializers import CompetitionSerializer, PrivateCompetitionSerializer
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