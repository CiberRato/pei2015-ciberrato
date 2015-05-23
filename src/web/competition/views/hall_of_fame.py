from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db import IntegrityError
from django.db import transaction

from rest_framework import permissions
from rest_framework import status, views, viewsets, mixins
from rest_framework.response import Response

import requests

from ..permissions import MustBePartOfAgentTeam, CompetitionMustBeNotInPast, MustBeHallOfFameCompetition
from ..models import Round, Trial, CompetitionAgent, LogTrialAgent, Agent, Competition, AgentScoreRound
from ..serializers import HallOfFameLaunchSerializer, AutomaticTeamScoreHallOfFameSerializer, HallOfFameSerializer
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
            r = trial.round
            score = serializer.validated_data['score']
            number_of_agents = serializer.validated_data['number_of_agents']
            time = serializer.validated_data['time']

            try:
                with transaction.atomic():
                    AgentScoreRound.objects.create(trial=trial,
                                                   team=team,
                                                   round=r,
                                                   score=score,
                                                   number_of_agents=number_of_agents,
                                                   time=time)
            except IntegrityError:
                # see if the new score is higher than the old one
                old = AgentScoreRound.objects.get(round=r, team=team)

                if AutomaticTeamScoreHallOfFame.new_is_higher_than_old_one(old=old, score=score, time=time,
                                                                           number_of_agents=number_of_agents):
                    # if is higher, delete the old one
                    old.trial.delete()
                    old.delete()

                    # add the new one score
                    AgentScoreRound.objects.create(trial=trial,
                                                   team=team,
                                                   round=r,
                                                   score=score,
                                                   number_of_agents=number_of_agents,
                                                   time=time)
                else:
                    # if is not higher, so delete the new one trial
                    trial.delete()

            return Response({'status': 'OK',
                             'message': 'The score has been received!'}
                            , status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def new_is_higher_than_old_one(old, score, number_of_agents, time):
        assert isinstance(old, AgentScoreRound)
        if score > old.score:
            return True
        if score == old.score:
            if number_of_agents > old.score:
                return True
            if number_of_agents == old.score:
                if time < old.score:
                    return True
        return False


class HallOfFameScore(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = AgentScoreRound.objects.all()
    serializer_class = HallOfFameSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the hall of fame score
        B{URL:} ../api/v1/competitions/hall_of_fame/round_score/<round_name>/

        :type  round_name: str
        :param round_name: The round name
        """
        r = get_object_or_404(Round.objects.all(), name=kwargs.get('pk', ''))
        scores = AgentScoreRound.objects.filter(round=r)
        serializer = self.serializer_class(data=scores, many=True)

        return Response(serializer.data)
