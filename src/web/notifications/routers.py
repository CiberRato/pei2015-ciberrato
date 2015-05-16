from swampdragon import route_handler
from swampdragon.route_handler import ModelPubRouter
from .models import NotificationUser, NotificationTeam, NotificationBroadcast
from .serializers import NotificationUserSerializer, NotificationTeamSerializer, NotificationBroadcastSerializer
from authentication.models import Team, TeamMember
from .permissions import LoginRequired, IsTeamMember


class NotificationBroadcastRouter(ModelPubRouter):
    permission_classes = [LoginRequired()]

    valid_verbs = ['subscribe']
    route_name = 'broadcast'
    model = NotificationBroadcast
    serializer_class = NotificationBroadcastSerializer

    def get_subscription_contexts(self, **kwargs):
        try:
            user_obj = self.connection.get_user(kwargs['user']['u_stream'])
        except AttributeError:
            return self.send_login_required()

        if user_obj is None:
            return self.send_login_required()

        NotificationBroadcast.objects.all().delete()

        if user_obj.is_staff == 1:
            return {'broadcast': 1}
        else:
            return {'broadcast': 0}


class NotificationUserRouter(ModelPubRouter):
    permission_classes = [LoginRequired()]

    valid_verbs = ['subscribe']
    route_name = 'user'
    model = NotificationUser
    serializer_class = NotificationUserSerializer

    def get_subscription_contexts(self, **kwargs):
        try:
            user_obj = self.connection.get_user(kwargs['user']['u_stream'])
        except AttributeError:
            return self.send_login_required()

        if user_obj is None:
            return self.send_login_required()

        NotificationUser.objects.all().delete()

        return {'user_id': user_obj.pk}


class NotificationTeamRouter(ModelPubRouter):
    permission_classes = [IsTeamMember()]

    valid_verbs = ['subscribe']
    route_name = 'team'
    model = NotificationTeam
    serializer_class = NotificationTeamSerializer

    def get_subscription_contexts(self, **kwargs):
        try:
            user_obj = self.connection.get_user(kwargs['user']['u_stream'])
        except AttributeError:
            return self.send_login_required()

        if user_obj is None:
            return self.send_login_required()

        if Team.objects.filter(name=kwargs['team']).count() == 1:
            team_obj = Team.objects.get(name=kwargs['team'])

            if TeamMember.objects.filter(team=team_obj, account=user_obj).count() == 1:
                NotificationTeam.objects.all().delete()
                return {'team_id': team_obj.pk}

        return self.send_login_required()


route_handler.register(NotificationUserRouter)
route_handler.register(NotificationTeamRouter)
route_handler.register(NotificationBroadcastRouter)