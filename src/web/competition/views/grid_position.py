from django.shortcuts import get_object_or_404, get_list_or_404

from rest_framework import permissions
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from authentication.models import Group, GroupMember
from agent.simplex import AgentSimplex
from agent.serializers import AgentSerializer

from ..permissions import IsAdmin
from .simplex import RoundSimplex, GridPositionsSimplex
from ..models import Competition, TypeOfCompetition, GridPositions, GroupEnrolled, AgentGrid, Agent
from ..serializers import CompetitionSerializer, CompetitionInputSerializer, RoundSerializer, \
    CompetitionStateSerializer, TypeOfCompetitionSerializer, GridPositionsSerializer, AgentGridSerializer


class GridPositionsViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                           mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = GridPositions.objects.all()
    serializer_class = GridPositionsSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def list(self, request, *args, **kwargs):
        """
        B{List} a grid position
        B{URL:} ../api/v1/competitions/grid_positions/
        """
        grid_positions = []
        for group in request.user.groups.all():
            for grid in GridPositions.objects.filter(group=group):
                grid_positions += [GridPositionsSimplex(grid)]

        serializer = self.serializer_class(grid_positions, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        B{Create} a grid positions
        B{URL:} ../api/v1/competitions/grid_positions/

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

            grid = GridPositions.objects.create(competition=competition, group=group)

            serializer = self.serializer_class(GridPositionsSimplex(grid))

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': 'The grid positions could not be created with received data'},
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

        grid = get_object_or_404(GridPositions.objects.all(), competition=competition, group=group)

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

        grid = get_object_or_404(GridPositions.objects.all(), competition=competition, group=group)
        grid.delete()

        return Response({'status': 'Deleted',
                         'message': 'The grid positions has been deleted'},
                        status=status.HTTP_200_OK)


class AgentGridViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                       mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = AgentGrid.objects.all()
    serializer_class = AgentGridSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def create(self, request, *args, **kwargs):
        """
        B{Associate} agent to the grid position
        B{URL:} ../api/v1/competitions/agent_grid/

        @type  grid_identifier: str
        @param grid_identifier: The grid identifier
        @type  agent_name: str
        @type  agent_name: The agent name
        @type  position: Integer
        @type  position: The agent position
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            agent = get_object_or_404(Agent.objects.all(), agent_name=serializer.validated_data['agent_name'])

            if agent.group not in request.user.groups.all():
                return Response({'status': 'Bad Request',
                                 'message': 'You must be part of the agent group.'},
                                status=status.HTTP_400_BAD_REQUEST)

            grid = get_object_or_404(GridPositions.objects.all(),
                identifier=serializer.validated_data['grid_identifier'])

            agents_in_grid = len(AgentGrid.objects.filter(grid_position=grid))

            if agents_in_grid >= grid.competition.type_of_competition.number_agents_by_grid:
                return Response({'status': 'Bad Request',
                                 'message': 'You can not add more agents to the grid.'},
                                status=status.HTTP_400_BAD_REQUEST)

            if grid.competition.state_of_competition == 'Past':
                return Response({'status': 'Bad Request',
                                 'message': 'The competition is in \'Past\' state.'},
                                status=status.HTTP_400_BAD_REQUEST)

            group_enrolled = GroupEnrolled.objects.filter(group=agent.group, competition=grid.competition)

            if len(group_enrolled) != 1:
                return Response({'status': 'Permission denied',
                                 'message': 'Your group must be enrolled in the competition.'},
                                status=status.HTTP_403_FORBIDDEN)

            if not group_enrolled[0].valid:
                return Response({'status': 'Permission denied',
                                 'message': 'Your group must be enrolled in the competition with valid inscription.'},
                                status=status.HTTP_403_FORBIDDEN)

            if serializer.validated_data['position'] > grid.competition.type_of_competition.number_agents_by_grid:
                return Response({'status': 'Permission denied',
                                 'message': 'The position can\'t be higher than the number agents allowed by grid.'},
                                status=status.HTTP_403_FORBIDDEN)

            if len(AgentGrid.objects.filter(grid_position=grid, position=serializer.validated_data['position'])) != 0:
                return Response({'status': 'Permission denied',
                                 'message': 'The position has already been taken.'},
                                status=status.HTTP_403_FORBIDDEN)

            AgentGrid.objects.create(agent=agent, grid_position=grid, position=serializer.validated_data['position'])

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': 'You can\'t associate the agent to the Grid with the received data'},
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} agents by grid
        B{URL:} ../api/v1/competitions/agent_grid/<grid_identifier>/

        @type  grid_identifier: str
        @param grid_identifier: The grid identifier
        """
        grid = get_object_or_404(GridPositions.objects.all(), identifier=kwargs.get('pk', ''))
        agents_grid = AgentGrid.objects.filter(grid_position=grid)

        agents = [AgentSimplex(agent.agent) for agent in agents_grid]

        serializer = AgentSerializer(agents, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        B{Delete} the agent in the grid
        B{URL:} ../api/v1/competitions/agent_grid/<grid_identifier>/?position=<position>

        @type  grid_identifier: str
        @param grid_identifier: The grid identifier
        @type  agent_name: str
        @type  agent_name: The agent name
        """
        grid = get_object_or_404(GridPositions.objects.all(), identifier=kwargs.get('pk', ''))
        agent_grid = get_object_or_404(AgentGrid.objects.all(), grid_position=grid,
            position=request.GET.get('position', ''))

        agent = agent_grid.agent

        if agent.group not in request.user.groups.all():
            return Response({'status': 'Bad Request',
                             'message': 'You must be part of the agent group.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if grid.competition.state_of_competition == 'Past':
            return Response({'status': 'Bad Request',
                             'message': 'The competition is in \'Past\' state.'},
                            status=status.HTTP_400_BAD_REQUEST)

        group_enrolled = GroupEnrolled.objects.filter(group=agent.group, competition=grid.competition)

        if len(group_enrolled) != 1:
            return Response({'status': 'Permission denied',
                             'message': 'Your group must be enrolled in the competition.'},
                            status=status.HTTP_403_FORBIDDEN)

        if not group_enrolled[0].valid:
            return Response({'status': 'Permission denied',
                             'message': 'Your group must be enrolled in the competition with valid inscription.'},
                            status=status.HTTP_403_FORBIDDEN)

        agent_grid.delete()

        return Response({'status': 'Deleted',
                         'message': 'The agent has been dissociated!'},
                        status=status.HTTP_200_OK)
