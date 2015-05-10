import uuid

from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db import transaction
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework import permissions
from rest_framework import viewsets, status, mixins, views
from rest_framework.response import Response
from .models import StickyNote
from .serializers import StickyNoteSerializer
from competition.permissions import IsStaff


class StickyNotesViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                         mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = StickyNote.objects.filter(active=True)
    serializer_class = StickyNoteSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(), IsStaff(),

    def list(self, request, *args, **kwargs):
        """
        B{List} the active sticky notes
        B{URL:} ../api/v1/sticky_notes/crud/
        """
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        B{Create} an sticky note
        B{URL:} ../api/v1/competitions/grid_positions/

        :type  competition_name: str
        :param competition_name: The type of competition name
        :type  team_name: str
        :type  team_name: The team name
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            competition = get_object_or_404(Competition.objects.all(),
                                            name=serializer.validated_data['competition_name'])

            if competition.state_of_competition == 'Past':
                return Response({'status': 'Bad Request',
                                 'message': 'The competition is in \'Past\' state.'},
                                status=status.HTTP_400_BAD_REQUEST)

            team = get_object_or_404(Team.objects.all(), name=serializer.validated_data['team_name'])

            if len(TeamMember.objects.filter(team=team, account=request.user)) != 1:
                return Response({'status': 'Permission denied',
                                 'message': 'You must be part of the team.'},
                                status=status.HTTP_403_FORBIDDEN)

            team_enrolled = TeamEnrolled.objects.filter(team=team, competition=competition)
            if len(team_enrolled) != 1:
                return Response({'status': 'Permission denied',
                                 'message': 'Your team must be enrolled in the competition.'},
                                status=status.HTTP_403_FORBIDDEN)

            if not team_enrolled[0].valid:
                return Response({'status': 'Permission denied',
                                 'message': 'Your team must be enrolled in the competition with valid inscription.'},
                                status=status.HTTP_403_FORBIDDEN)

            try:
                with transaction.atomic():
                    grid = GridPositions.objects.create(competition=competition, team=team)
            except IntegrityError:
                return Response({'status': 'Bad request',
                                 'message': 'You already have a grid for that competition.'},
                                status=status.HTTP_400_BAD_REQUEST)

            serializer = self.serializer_class(GridPositionsSimplex(grid))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the grid positions details
        B{URL:} ../api/v1/competitions/grid_positions/<competition_name>/?team_name=<team_name>

        :type  competition_name: str
        :param competition_name: The type of competition name
        :type  team_name: str
        :type  team_name: The team name
        """
        competition = get_object_or_404(Competition.objects.all(), name=kwargs.get('pk', ''))

        if competition.state_of_competition == 'Past':
            return Response({'status': 'Bad Request',
                             'message': 'The competition is in \'Past\' state.'},
                            status=status.HTTP_400_BAD_REQUEST)

        team = get_object_or_404(Team.objects.all(), name=request.GET.get('team_name', ''))

        if len(TeamMember.objects.filter(team=team, account=request.user)) != 1:
            return Response({'status': 'Permission denied',
                             'message': 'You must be part of the team.'},
                            status=status.HTTP_403_FORBIDDEN)

        team_enrolled = TeamEnrolled.objects.filter(team=team, competition=competition)
        if len(team_enrolled) != 1:
            return Response({'status': 'Permission denied',
                             'message': 'Your team must be enrolled in the competition.'},
                            status=status.HTTP_403_FORBIDDEN)

        if not team_enrolled[0].valid:
            return Response({'status': 'Permission denied',
                             'message': 'Your team must be enrolled in the competition with valid inscription.'},
                            status=status.HTTP_403_FORBIDDEN)

        grid = get_object_or_404(GridPositions.objects.all(), competition=competition, team=team)

        serializer = self.serializer_class(GridPositionsSimplex(grid))

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} the grid positions
        B{URL:} ../api/v1/competitions/grid_positions/<competition_name>/?team_name=<team_name>

        :type  competition_name: str
        :param competition_name: The type of competition name
        :type  team_name: str
        :type  team_name: The team name
        """
        competition = get_object_or_404(Competition.objects.all(), name=kwargs.get('pk', ''))

        if competition.state_of_competition == 'Past':
            return Response({'status': 'Bad Request',
                             'message': 'The competition is in \'Past\' state.'},
                            status=status.HTTP_400_BAD_REQUEST)

        team = get_object_or_404(Team.objects.all(), name=request.GET.get('team_name', ''))

        if len(TeamMember.objects.filter(team=team, account=request.user)) != 1:
            return Response({'status': 'Permission denied',
                             'message': 'You must be part of the team.'},
                            status=status.HTTP_403_FORBIDDEN)

        team_enrolled = TeamEnrolled.objects.filter(team=team, competition=competition)
        if len(team_enrolled) != 1:
            return Response({'status': 'Permission denied',
                             'message': 'Your team must be enrolled in the competition.'},
                            status=status.HTTP_403_FORBIDDEN)

        if not team_enrolled[0].valid:
            return Response({'status': 'Permission denied',
                             'message': 'Your team must be enrolled in the competition with valid inscription.'},
                            status=status.HTTP_403_FORBIDDEN)

        grid = get_object_or_404(GridPositions.objects.all(), competition=competition, team=team)

        if grid.competition.type_of_competition.name == settings.PRIVATE_COMPETITIONS_NAME:
            return Response({'status': 'Bad Request',
                             'message': 'This grid can\'t be deleted!'},
                            status=status.HTTP_400_BAD_REQUEST)

        grid.delete()

        return Response({'status': 'Deleted',
                         'message': 'The grid positions has been deleted'},
                        status=status.HTTP_200_OK)