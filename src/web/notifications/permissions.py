from swampdragon.permissions import RoutePermission
from authentication.models import Team, TeamMember


class LoginRequired(RoutePermission):
    def __init__(self, verbs=None):
        self.test_against_verbs = verbs

    def test_permission(self, handler, verb, **kwargs):
        if 'user' not in kwargs or 'u_stream' not in kwargs['user']:
            return False
        try:
            return handler.connection.authenticate(kwargs['user']['u_stream'])
        except AttributeError:
            return False

    def permission_failed(self, handler):
        handler.send_login_required()


class IsTeamMember(RoutePermission):
    def __init__(self, verbs=None):
        self.test_against_verbs = verbs

    def test_permission(self, handler, verb, **kwargs):
        if 'user' not in kwargs or 'team' not in kwargs:
            return False

        try:
            user_obj = handler.connection.get_user(kwargs['user']['u_stream'])
        except AttributeError:
            return False

        if user_obj is None:
                return False

        if Team.objects.filter(name=kwargs['team']).count() == 1:
            team_obj = Team.objects.get(name=kwargs['team'])
            return TeamMember.objects.filter(team=team_obj, account=user_obj).count() == 1

    def permission_failed(self, handler):
        handler.send_login_required()
