from rest_framework import permissions
from ciberonline.exceptions import BadRequest, Forbidden
from .models import TeamEnrolled
from django.conf import settings


class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user:
            return request.user.is_staff
        return False


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user:
            return request.user.is_superuser
        return False


class CompetitionMustBeNotInPast:
    def __init__(self, competition):
        if competition.state_of_competition == 'Past':
            raise BadRequest('The competition is in \'Past\' state.')


class TeamEnrolledWithValidInscription:
    def __init__(self, team, competition):
        team_enrolled = TeamEnrolled.objects.filter(team=team, competition=competition)
        if len(team_enrolled) != 1:
            raise Forbidden('Your team must be enrolled in the competition.')

        if not team_enrolled[0].valid:
            raise Forbidden('Your team must be enrolled in the competition with valid inscription.')


class NotPrivateCompetition:
    def __init__(self, competition, message='This competition can\'t be seen!'):
        if competition.type_of_competition.name == settings.PRIVATE_COMPETITIONS_NAME:
            raise BadRequest(message)


class MustBePartOfAgentTeam:
    def __init__(self, user, agent, message='You must be part of the agent team.'):
        if agent.team not in user.teams.all():
            raise BadRequest(message)


class NotAcceptingRemoteAgents:
    def __init__(self, competition, agent, message='The competition is not accepting remote agents!'):
        if not competition.type_of_competition.allow_remote_agents and agent.is_remote:
            raise BadRequest(message)


class MustBePrivateCompetition:
    def __init__(self, competition, message='You can only see this for private competitions!'):
        if competition.type_of_competition.name != settings.PRIVATE_COMPETITIONS_NAME:
            raise BadRequest(message)


class UserCanAccessToThePrivateCompetition:
    def __init__(self, user, competition, message='You can not see the rounds for this competition!'):
        team_enrolled = TeamEnrolled.objects.filter(competition=competition).first()
        if team_enrolled.team not in user.teams.all():
            BadRequest(message)


class NotHallOfFameCompetition:
    def __init__(self, competition, message='This competition can\'t be seen!'):
        if competition.type_of_competition.name.startswith(settings.HALL_OF_FAME_START_STR):
            raise BadRequest(message)


class MustBeHallOfFameCompetition:
    def __init__(self, competition, message='You can only start the simulation for the Hall of fame!'):
        if not competition.type_of_competition.name.startswith(settings.HALL_OF_FAME_START_STR):
            raise BadRequest(message)


class ReservedName:
    def __init__(self, name, reserved, message='This type of competition name is reserved!', starts=False):
        if not starts:
            if name == reserved:
                raise BadRequest(message)
        else:
            if name.startswith(reserved):
                raise BadRequest(message)


