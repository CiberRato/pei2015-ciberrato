from ciberonline.exceptions import Forbidden
from authentication.models import TeamMember


class MustBeTeamMember:
    def __init__(self, user, team, message="You must be part of the team."):
        team_member = TeamMember.objects.filter(team=team, account=user)

        if len(team_member) == 0:
            raise Forbidden(message)