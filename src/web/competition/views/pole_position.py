from django.shortcuts import get_object_or_404, get_list_or_404

from rest_framework import permissions
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from authentication.models import Group, GroupMember

from ..permissions import IsAdmin
from .simplex import RoundSimplex, PoleSimplex
from ..models import Competition, TypeOfCompetition, PolePosition, GroupEnrolled, AgentPole
from ..serializers import CompetitionSerializer, CompetitionInputSerializer, RoundSerializer, \
    CompetitionStateSerializer, TypeOfCompetitionSerializer, PolePositionSerializer, AgentPoleSerializer


class PolePositionViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                          mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = PolePosition.objects.all()
    serializer_class = PolePositionSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def list(self, request, *args, **kwargs):
        """
        B{List} a pole position
        B{URL:} ../api/v1/competitions/pole_position/
        """
        pole_positions = []
        for group in request.user.groups.all():
            for pole in PolePosition.objects.filter(group=group):
                pole_positions += [PoleSimplex(pole)]

        serializer = self.serializer_class(pole_positions, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        B{Create} a pole position
        B{URL:} ../api/v1/competitions/pole_position/

        @type  competition_name: str
        @param competition_name: The type of competition name
        @type  group_name: str
        @type  group_name: The group name
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            competition = get_object_or_404(Competition.objects.all(),
                                            name=serializer.validated_data['competition_name'])

            if competition.state_of_competition == 'Past':
                return Response({'status': 'Bad Request',
                                 'message': 'The competition is in \'Past\' state.'},
                                status=status.HTTP_400_BAD_REQUEST)

            group = get_object_or_404(Group.objects.all(), name=serializer.validated_data['group_name'])

            if len(GroupMember.objects.filter(group=group, account=request.user)) != 1:
                return Response({'status': 'Permission denied',
                                 'message': 'You must be part of the group.'},
                                status=status.HTTP_403_FORBIDDEN)

            group_enrolled = GroupEnrolled.objects.filter(group=group, competition=competition)
            if len(group_enrolled) != 1:
                return Response({'status': 'Permission denied',
                                 'message': 'Your group must be enrolled in the competition.'},
                                status=status.HTTP_403_FORBIDDEN)

            if not group_enrolled[0].valid:
                return Response({'status': 'Permission denied',
                                 'message': 'Your group must be enrolled in the competition with valid inscription.'},
                                status=status.HTTP_403_FORBIDDEN)

            pole = PolePosition.objects.create(competition=competition, group=group)

            serializer = self.serializer_class(PoleSimplex(pole))

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': 'The pole position could not be created with received data'},
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the pole details
        B{URL:} ../api/v1/competitions/pole_position/<competition_name>/?group_name=<group_name>

        @type  competition_name: str
        @param competition_name: The type of competition name
        @type  group_name: str
        @type  group_name: The group name
        """
        competition = get_object_or_404(Competition.objects.all(), name=kwargs.get('pk', ''))

        if competition.state_of_competition == 'Past':
            return Response({'status': 'Bad Request',
                             'message': 'The competition is in \'Past\' state.'},
                            status=status.HTTP_400_BAD_REQUEST)

        group = get_object_or_404(Group.objects.all(), name=request.GET.get('group_name', ''))

        if len(GroupMember.objects.filter(group=group, account=request.user)) != 1:
            return Response({'status': 'Permission denied',
                             'message': 'You must be part of the group.'},
                            status=status.HTTP_403_FORBIDDEN)

        group_enrolled = GroupEnrolled.objects.filter(group=group, competition=competition)
        if len(group_enrolled) != 1:
            return Response({'status': 'Permission denied',
                             'message': 'Your group must be enrolled in the competition.'},
                            status=status.HTTP_403_FORBIDDEN)

        if not group_enrolled[0].valid:
            return Response({'status': 'Permission denied',
                             'message': 'Your group must be enrolled in the competition with valid inscription.'},
                            status=status.HTTP_403_FORBIDDEN)

        pole = get_object_or_404(PolePosition.objects.all(), competition=competition, group=group)

        serializer = self.serializer_class(PoleSimplex(pole))

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} the pole position
        B{URL:} ../api/v1/competitions/pole_position/<competition_name>/?group_name=<group_name>

        @type  competition_name: str
        @param competition_name: The type of competition name
        @type  group_name: str
        @type  group_name: The group name
        """
        competition = get_object_or_404(Competition.objects.all(), name=kwargs.get('pk', ''))

        if competition.state_of_competition == 'Past':
            return Response({'status': 'Bad Request',
                             'message': 'The competition is in \'Past\' state.'},
                            status=status.HTTP_400_BAD_REQUEST)

        group = get_object_or_404(Group.objects.all(), name=request.GET.get('group_name', ''))

        if len(GroupMember.objects.filter(group=group, account=request.user)) != 1:
            return Response({'status': 'Permission denied',
                             'message': 'You must be part of the group.'},
                            status=status.HTTP_403_FORBIDDEN)

        group_enrolled = GroupEnrolled.objects.filter(group=group, competition=competition)
        if len(group_enrolled) != 1:
            return Response({'status': 'Permission denied',
                             'message': 'Your group must be enrolled in the competition.'},
                            status=status.HTTP_403_FORBIDDEN)

        if not group_enrolled[0].valid:
            return Response({'status': 'Permission denied',
                             'message': 'Your group must be enrolled in the competition with valid inscription.'},
                            status=status.HTTP_403_FORBIDDEN)

        pole = get_object_or_404(PolePosition.objects.all(), competition=competition, group=group)
        pole.delete()

        return Response({'status': 'Deleted',
                         'message': 'The pole position has been deleted'},
                        status=status.HTTP_200_OK)


class AssociateAgentToPole(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = AgentPole.objects.all()
    serializer_class = AgentPoleSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def create(self, request, *args, **kwargs):
        """
        B{Create} a pole position
        B{URL:} ../api/v1/competitions/associate_agent_pole/

        @type  competition_name: str
        @param competition_name: The type of competition name
        @type  agent_name: str
        @type  agent_name: The agent name
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            competition = get_object_or_404(Competition.objects.all(),
                name=serializer.validated_data['competition_name'])

            if competition.state_of_competition == 'Past':
                return Response({'status': 'Bad Request',
                                 'message': 'The competition is in \'Past\' state.'},
                                status=status.HTTP_400_BAD_REQUEST)

            group = get_object_or_404(Group.objects.all(), name=serializer.validated_data['group_name'])

            if len(GroupMember.objects.filter(group=group, account=request.user)) != 1:
                return Response({'status': 'Permission denied',
                                 'message': 'You must be part of the group.'},
                                status=status.HTTP_403_FORBIDDEN)

            group_enrolled = GroupEnrolled.objects.filter(group=group, competition=competition)
            if len(group_enrolled) != 1:
                return Response({'status': 'Permission denied',
                                 'message': 'Your group must be enrolled in the competition.'},
                                status=status.HTTP_403_FORBIDDEN)

            if not group_enrolled[0].valid:
                return Response({'status': 'Permission denied',
                                 'message': 'Your group must be enrolled in the competition with valid inscription.'},
                                status=status.HTTP_403_FORBIDDEN)

            PolePosition.objects.create(competition=competition, group=group)

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': 'The pole position could not be created with received data'},
                        status=status.HTTP_400_BAD_REQUEST)