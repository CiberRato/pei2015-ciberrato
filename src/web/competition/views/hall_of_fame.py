from django.shortcuts import get_object_or_404
from django.conf import settings

from rest_framework import permissions
from rest_framework import status, views
from rest_framework.response import Response

import requests

from ..permissions import MustBeHallOfFameCompetition, MustBePartOfAgentTeam
from ..models import Round, Trial, \
    CompetitionAgent, LogTrialAgent, Agent


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

        :type  round_name: str
        :param round_name: The round name
        :type  agent_name: str
        :type  agent_name: The team name
        """
        # get round
        r = get_object_or_404(Round.objects.all(), name=request.data.get('round_name', ''))

        # verify if the round is from a private competition
        MustBeHallOfFameCompetition(competition=r.parent_competition)

        # agent
        agent = get_object_or_404(Agent.objects.all(), agent_name=request.data.get('agent_name', ''))

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