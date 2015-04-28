from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db import transaction

from rest_framework import permissions
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from authentication.models import Team, TeamMember

from .simplex import GridPositionsSimplex, AgentGridSimplex
from ..models import Competition, GridPositions, TeamEnrolled, AgentGrid, Agent, TrialGrid
from ..serializers import GridPositionsSerializer, AgentGridSerializer, AgentRemoteGridSerializer
from ..permissions import IsStaff


class GridPositionsViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                           mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = GridPositions.objects.all()
    serializer_class = GridPositionsSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def list(self, request, *args, **kwargs):
        """
        B{List} user grid position
        B{URL:} ../api/v1/competitions/grid_positions/
        """
        grid_positions = []
        for team in request.user.teams.all():
            for grid in GridPositions.objects.filter(team=team):
                grid_positions += [GridPositionsSimplex(grid)]

        serializer = self.serializer_class(grid_positions, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        B{Create} a grid positions
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

                    serializer = self.serializer_class(GridPositionsSimplex(grid))

                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({'status': 'Bad request',
                                 'message': 'You already have a grid for that competition.'},
                                status=status.HTTP_400_BAD_REQUEST)

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

        :type  grid_identifier: str
        :param grid_identifier: The grid identifier
        :type  agent_name: str
        :param agent_name: The agent name
        :type  team_name: str
        :param team_name: The team name
        :type  position: Integer
        :param  position: The agent position
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            team = get_object_or_404(Team.objects.all(), name=serializer.validated_data['team_name'])
            agent = get_object_or_404(Agent.objects.all(), team=team,
                                      agent_name=serializer.validated_data['agent_name'])

            if team not in request.user.teams.all():
                return Response({'status': 'Bad Request',
                                 'message': 'You must be part of the agent team.'},
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

            if not grid.competition.allow_remote_agents and agent.is_remote:
                return Response({'status': 'Bad Request',
                                 'message': 'The competition is not accepting remote agents!'},
                                status=status.HTTP_400_BAD_REQUEST)

            team_enrolled = TeamEnrolled.objects.filter(team=team, competition=grid.competition)

            if len(team_enrolled) != 1:
                return Response({'status': 'Permission denied',
                                 'message': 'Your team must be enrolled in the competition.'},
                                status=status.HTTP_403_FORBIDDEN)

            if not team_enrolled[0].valid:
                return Response({'status': 'Permission denied',
                                 'message': 'Your team must be enrolled in the competition with valid inscription.'},
                                status=status.HTTP_403_FORBIDDEN)

            if serializer.validated_data['position'] > grid.competition.type_of_competition.number_agents_by_grid:
                return Response({'status': 'Bad Request',
                                 'message': 'The position can\'t be higher than the number agents allowed by grid.'},
                                status=status.HTTP_400_BAD_REQUEST)

            if len(AgentGrid.objects.filter(grid_position=grid, position=serializer.validated_data['position'])) != 0:
                return Response({'status': 'Bad Request',
                                 'message': 'The position has already been taken.'},
                                status=status.HTTP_400_BAD_REQUEST)
            try:
                with transaction.atomic():
                    AgentGrid.objects.create(agent=agent, grid_position=grid, position=serializer.validated_data['position'])
            except IntegrityError:
                return Response({'status': 'Bad request',
                                 'message': 'The agent can not be associated!'},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} agents by grid
        B{URL:} ../api/v1/competitions/agent_grid/<grid_identifier>/

        :type  grid_identifier: str
        :param grid_identifier: The grid identifier
        """
        grid = get_object_or_404(GridPositions.objects.all(), identifier=kwargs.get('pk', ''))
        agents_grid = AgentGrid.objects.filter(grid_position=grid)

        serializer = self.serializer_class([AgentGridSimplex(agent_grid) for agent_grid in agents_grid], many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        B{Delete} the agent in the grid
        B{URL:} ../api/v1/competitions/agent_grid/<grid_identifier>/?position=<position>

        :type  grid_identifier: str
        :param grid_identifier: The grid identifier
        :type  position: str
        :type  position: The position
        """
        grid = get_object_or_404(GridPositions.objects.all(), identifier=kwargs.get('pk', ''))
        agent_grid = get_object_or_404(AgentGrid.objects.all(), grid_position=grid,
            position=request.GET.get('position', ''))

        agent = agent_grid.agent

        if agent.team not in request.user.teams.all():
            return Response({'status': 'Bad Request',
                             'message': 'You must be part of the agent team.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if grid.competition.state_of_competition == 'Past':
            return Response({'status': 'Bad Request',
                             'message': 'The competition is in \'Past\' state.'},
                            status=status.HTTP_400_BAD_REQUEST)

        team_enrolled = TeamEnrolled.objects.filter(team=agent.team, competition=grid.competition)

        if len(team_enrolled) != 1:
            return Response({'status': 'Permission denied',
                             'message': 'Your team must be enrolled in the competition.'},
                            status=status.HTTP_403_FORBIDDEN)

        if not team_enrolled[0].valid:
            return Response({'status': 'Permission denied',
                             'message': 'Your team must be enrolled in the competition with valid inscription.'},
                            status=status.HTTP_403_FORBIDDEN)

        # if has no robots and there is a TrialGrid it must be deleted
        if grid.agentgrid_set.count() == 0:
            TrialGrid.objects.filter(grid_positions=grid).delete()

        agent_grid.delete()

        return Response({'status': 'Deleted',
                         'message': 'The agent has been dissociated!'},
                        status=status.HTTP_200_OK)


class GridPositionsByCompetition(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = GridPositions.objects.all()
    serializer_class = GridPositionsSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(), IsStaff(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the grid positions by competition
        B{URL:} ../api/v1/competitions/grid_positions_competition/<competition_name>/

        :type  competition_name: str
        :param competition_name: The type of competition name
        """
        competition = get_object_or_404(Competition.objects.all(), name=kwargs.get('pk', ''))
        grids = GridPositions.objects.filter(competition=competition)

        grid_available = []

        for grid in grids:
            if AgentGrid.objects.filter(grid_position=grid).count() > 0:
                grid_available += [grid]

        serializer = self.serializer_class([GridPositionsSimplex(grid) for grid in grid_available], many=True)

        return Response(serializer.data)