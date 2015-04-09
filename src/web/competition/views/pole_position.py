from django.shortcuts import get_object_or_404

from rest_framework import permissions
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from authentication.models import Group, GroupMember

from ..permissions import IsAdmin
from .simplex import RoundSimplex
from ..models import Competition, TypeOfCompetition, PolePosition
from ..serializers import CompetitionSerializer, CompetitionInputSerializer, RoundSerializer, \
    CompetitionStateSerializer, TypeOfCompetitionSerializer, PolePositionSerializer


class PolePositionViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                          mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):

    queryset = PolePosition.objects.all()
    serializer_class = PolePositionSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def create(self, request, *args, **kwargs):
        """
        B{Create} type of competition
        B{URL:} ../api/v1/competitions/pole_position/

        @type  competition_name: str
        @param competition_name: The type of competition name
        @type  group_name: str
        @type  group_name: The group name
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            competition = get_object_or_404(Competition.objects.all(), name=serializer.validated_data['competition_name'])
            group = get_object_or_404(Group.objects.all(), name=serializer.validated_data['group_name'])
            PolePosition.objects.create(competition=competition, group=group)

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': 'The pole position could not be created with received data'},
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the type of competition
        B{URL:} ../api/v1/competitions/type_of_competition/<type_of_competition_name>/

        @type  type_of_competition_name: str
        @param type_of_competition_name: The type_of_competition name
        """
        queryset = TypeOfCompetition.objects.all()
        type_of_competition = get_object_or_404(queryset, name=kwargs.get('pk', ''))
        serializer = self.serializer_class(type_of_competition)

        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        B{Update} the type of competition
        B{URL:} ../api/v1/competitions/type_of_competition/<old_type_of_competition_name>/

        @type  old_name: str
        @param old_name: The type of competition name

        @type  name: str
        @param name: The type of competition name
        @type  number_teams_for_trial: Integer
        @type  number_teams_for_trial: The number of teams allowed by trial
        @type  number_agents_by_grid: Integer
        @param number_agents_by_grid: For each team the number of agents allowed by trial
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            type_of_competition = get_object_or_404(self.queryset, name=kwargs.get('pk', ''))
            type_of_competition.name = serializer.validated_data['name']
            type_of_competition.number_teams_for_trial = serializer.validated_data['number_teams_for_trial']
            type_of_competition.number_agents_by_grid = serializer.validated_data['number_agents_by_grid']
            type_of_competition.save()

            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        return Response({'status': 'Bad Request',
                         'message': 'The type of competition name could not be update with that information'},
                        status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} the type of competition
        B{URL:} ../api/v1/competitions/type_of_competition/<type_of_competition_name>/

        @type  type_of_competition_name: str
        @param type_of_competition_name: The type_of_competition name
        """
        queryset = TypeOfCompetition.objects.all()
        type_of_competition = get_object_or_404(queryset, name=kwargs.get('pk', ''))

        type_of_competition.delete()

        return Response({'status': 'Deleted',
                         'message': 'The type of competition has been deleted'},
                        status=status.HTTP_200_OK)