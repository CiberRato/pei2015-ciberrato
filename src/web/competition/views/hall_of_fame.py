from django.shortcuts import get_object_or_404
from django.conf import settings

from rest_framework import permissions
from rest_framework import status, views, viewsets, mixins
from rest_framework.response import Response

import requests

from ..permissions import MustBeHallOfFameCompetition, MustBePartOfAgentTeam
from ..models import Round, Trial, CompetitionAgent, LogTrialAgent, Agent, Competition, AgentScoreRound
from ..serializers import HallOfFameLaunchSerializer, AutomaticTeamScoreHallOfFameSerializer
from authentication.models import Team
from teams.permissions import MustBeTeamMember


class RunHallOfFameTrial(views.APIView):
    def get_permissions(self):
        return permissions.IsAuthenticated(),

    @staticmethod
    def post(request):
        """
        B{Launch} one trial for the hall of fame
        B{URL:} ../api/v1/competitions/hall_of_fame/launch_trial/

        > Permissions
        # Must be part of the team of the agent
        # Must be a Hall of fame competition

        :type   round_name: str
        :param  round_name: The round name
        :type   agent_name: str
        :param  agent_name: The agent name
        :type   team_name: The team name
        :param  team_name: The team name
        """
        serializer = HallOfFameLaunchSerializer(data=request.data)

        if serializer.is_valid():
            # get competition
            competition = get_object_or_404(Competition.objects.all(), name='Hall of fame - Single')

            # get round
            r = get_object_or_404(Round.objects.all(), name=serializer.validated_data['round_name'],
                                  parent_competition=competition)

            # verify if the round is from a hall of fame competition
            MustBeHallOfFameCompetition(competition=r.parent_competition)

            # team
            team = get_object_or_404(Team.objects.all(), name=serializer.validated_data['team_name'])

            # must be team member
            MustBeTeamMember(user=request.user, team=team)

            agent = get_object_or_404(Agent.objects.all(), agent_name=serializer.validated_data['agent_name'],
                                      team=team)

            # Must be part of the agent team
            MustBePartOfAgentTeam(agent=agent, user=request.user)

            # create trial for this round
            trial = Trial.objects.create(round=r)

            try:
                competition_agent = CompetitionAgent.objects.get(
                    competition=trial.round.parent_competition,
                    agent=agent,
                    round=trial.round)
            except CompetitionAgent.DoesNotExist:
                competition_agent = CompetitionAgent.objects.create(
                    competition=trial.round.parent_competition,
                    agent=agent,
                    round=trial.round)

            LogTrialAgent.objects.create(competition_agent=competition_agent,
                                         trial=trial,
                                         pos=1)

            params = {'trial_identifier': trial.identifier}

            try:
                requests.post(settings.PREPARE_SIM_ENDPOINT, params)
            except requests.ConnectionError:
                return Response({'status': 'Bad Request',
                                 'message': 'The simulator appears to be down!'},
                                status=status.HTTP_400_BAD_REQUEST)

            trial.waiting = True
            trial.prepare = False
            trial.started = False
            trial.save()

            return Response({'status': 'Trial started',
                             'message': 'The trial for the Hall Of Fame has been launched!'},
                            status=status.HTTP_200_OK)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class AutomaticTeamScoreHallOfFame(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = AgentScoreRound.objects.all()
    serializer_class = AutomaticTeamScoreHallOfFameSerializer

    def get_permissions(self):
        return permissions.AllowAny(),

    def create(self, request, *args, **kwargs):
        """
        B{Create} an automatic team score
        B{URL:} ../api/v1/competitions/hall_of_fame/automatic_score/

        SERVER - TO - SERVER ONLY

        :type  trial_id: str
        :param trial_id: The trial identifier
        :type  score: Integer
        :param score: The score
        :type  number_of_agents: Integer
        :param number_of_agents: The number of agents
        :type  time: Integer
        :param time: The time
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            trial = get_object_or_404(Trial.objects.all(), identifier=serializer.validated_data['trial_id'])

            CompetitionMustBeNotInPast(competition=trial.round.parent_competition)

            # for now only hall of fame has automatic scores
            MustBeHallOfFameCompetition(competition=trial.round.parent_competition,
                                        message="This is not a Hall of fame competition")

            agent = trial.logtrialagent_set.first()
            team = agent.team

            try:
                with transaction.atomic():
                    team_score = TeamScore.objects.create(trial=trial, team=team,
                                                          score=serializer.validated_data['score'],
                                                          number_of_agents=serializer.validated_data[
                                                              'number_of_agents'],
                                                          time=serializer.validated_data['time'])
            except IntegrityError:
                team_score = TeamScore.objects.get(trial=trial, team=team)
                team_score.score = serializer.validated_data['score']
                team_score.number_of_agents = serializer.validated_data['number_of_agents']
                team_score.time = serializer.validated_data['time']

            serializer = self.serializer_class(TeamScoreSimplex(team_score))
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)