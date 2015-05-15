from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db import transaction

from rest_framework import permissions
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from authentication.models import Team

from teams.permissions import MustBeTeamMember

from agent.permissions import AgentMustHaveValidCode

from .simplex import GridPositionsSimplex, AgentGridSimplex
from ..models import Competition, GridPositions, TeamEnrolled, AgentGrid, Agent, TrialGrid
from ..serializers import GridPositionsSerializer, AgentGridSerializer
from ..permissions import IsStaff, CompetitionMustBeNotInPast, TeamEnrolledWithValidInscription, \
    NotPrivateCompetition, MustBePartOfAgentTeam, NotAcceptingRemoteAgents


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
        for grid in GridPositions.objects.filter(team=request.user.teams.all()):
            grid_positions += [GridPositionsSimplex(grid)]

        serializer = self.serializer_class(grid_positions, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        B{Create} a grid positions
        B{URL:} ../api/v1/competitions/grid_positions/

        > Permissions
        # Must be part of the team
        # The competition must be not in past state
        # The team must be enrolled in the competition
        # The team must have a valid inscription

        :type  competition_name: str
        :param competition_name: The type of competition name
        :type  team_name: str
        :type  team_name: The team name
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            competition = get_object_or_404(Competition.objects.all(),
                                            name=serializer.validated_data['competition_name'])

            CompetitionMustBeNotInPast(competition=competition)

            team = get_object_or_404(Team.objects.all(), name=serializer.validated_data['team_name'])

            MustBeTeamMember(team=team, user=request.user)

            TeamEnrolledWithValidInscription(team=team, competition=competition)

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

        > Permissions
        # Must be part of the team
        # The competition must be not in past state
        # The team must be enrolled in the competition
        # The team must have a valid inscription

        :type  competition_name: str
        :param competition_name: The type of competition name
        :type  team_name: str
        :type  team_name: The team name
        """
        competition = get_object_or_404(Competition.objects.all(), name=kwargs.get('pk', ''))

        CompetitionMustBeNotInPast(competition=competition)

        team = get_object_or_404(Team.objects.all(), name=request.GET.get('team_name', ''))

        MustBeTeamMember(team=team, user=request.user)

        TeamEnrolledWithValidInscription(team=team, competition=competition)

        grid = get_object_or_404(GridPositions.objects.all(), competition=competition, team=team)

        serializer = self.serializer_class(GridPositionsSimplex(grid))

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} the grid positions
        B{URL:} ../api/v1/competitions/grid_positions/<competition_name>/?team_name=<team_name>

        > Permissions
        # Must be part of the team
        # The competition must be not in past state
        # The team must be enrolled in the competition
        # The team must have a valid inscription

        :type  competition_name: str
        :param competition_name: The type of competition name
        :type  team_name: str
        :type  team_name: The team name
        """
        competition = get_object_or_404(Competition.objects.all(), name=kwargs.get('pk', ''))

        CompetitionMustBeNotInPast(competition=competition)

        team = get_object_or_404(Team.objects.all(), name=request.GET.get('team_name', ''))

        MustBeTeamMember(team=team, user=request.user)

        TeamEnrolledWithValidInscription(team=team, competition=competition)

        grid = get_object_or_404(GridPositions.objects.all(), competition=competition, team=team)

        NotPrivateCompetition(competition=grid.competition, message='This grid can\'t be deleted!')

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

        > Permissions
        # Must be part of the team
        # The competition must be not in past state
        # The team must be enrolled in the competition
        # The team must have a valid inscription
        # The user must be enrolled in the team of the agent
        # The competition is NotAcceptingRemoteAgents
        # Agent must have the code valid

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

            MustBeTeamMember(user=request.user, team=team)

            MustBePartOfAgentTeam(user=request.user, agent=agent)

            AgentMustHaveValidCode(agent=agent)

            grid = get_object_or_404(GridPositions.objects.all(),
                                     identifier=serializer.validated_data['grid_identifier'])

            agents_in_grid = len(AgentGrid.objects.filter(grid_position=grid))

            if agents_in_grid >= grid.competition.type_of_competition.number_agents_by_grid:
                return Response({'status': 'Bad Request',
                                 'message': 'You can not add more agents to the grid.'},
                                status=status.HTTP_400_BAD_REQUEST)

            CompetitionMustBeNotInPast(competition=grid.competition)

            NotAcceptingRemoteAgents(competition=grid.competition, agent=agent)

            TeamEnrolledWithValidInscription(team=team, competition=grid.competition)

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

         > Permissions
        # The competition must be not in past state
        # The team must be enrolled in the competition
        # The team must have a valid inscription
        # The user must be enrolled in the team of the agent

        :type  grid_identifier: str
        :param grid_identifier: The grid identifier
        :type  position: str
        :type  position: The position
        """
        grid = get_object_or_404(GridPositions.objects.all(), identifier=kwargs.get('pk', ''))
        agent_grid = get_object_or_404(AgentGrid.objects.all(), grid_position=grid,
                                       position=request.GET.get('position', ''))

        MustBePartOfAgentTeam(agent=agent_grid.agent, user=request.user)
        CompetitionMustBeNotInPast(competition=grid.competition)
        TeamEnrolledWithValidInscription(team=agent_grid.agent.team, competition=grid.competition)

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