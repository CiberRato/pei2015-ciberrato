from swampdragon import route_handler
from swampdragon.route_handler import ModelPubRouter, BaseModelRouter
from .models import NotificationUser, NotificationTeam, NotificationBroadcast, StreamTrial
from .serializers import NotificationUserSerializer, NotificationTeamSerializer, NotificationBroadcastSerializer, \
    StreamTrialSerializer
from authentication.models import Team, TeamMember
from .permissions import LoginRequired, IsTeamMember
from competition.models import Trial
from competition.shortcuts import trial_started


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


class NotificationTeamRouter(BaseModelRouter):
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

    def delete(self, **kwargs):
        obj = self._get_object(**kwargs)
        obj.delete()

    def deleted(self, obj, obj_id, **kwargs):
        pass


class TrialRouter(ModelPubRouter):
    permission_classes = [LoginRequired()]

    valid_verbs = ['subscribe']
    route_name = 'stream_trial'
    model = StreamTrial
    serializer_class = StreamTrialSerializer

    def get_subscription_contexts(self, **kwargs):
        try:
            user_obj = self.connection.get_user(kwargs['user']['u_stream'])
        except AttributeError:
            return self.send_login_required()

        if user_obj is None:
            return self.send_login_required()

        if Trial.objects.filter(identifier=kwargs['identifier']).count() == 1:
            trial_obj = Trial.objects.get(identifier=kwargs['identifier'])

            if trial_started(trial_obj):
                StreamTrial.objects.all().delete()
                return {'trial_id': trial_obj.pk}

        return self.send_login_required()


route_handler.register(NotificationUserRouter)
route_handler.register(NotificationTeamRouter)
route_handler.register(NotificationBroadcastRouter)
route_handler.register(TrialRouter)