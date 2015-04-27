from swampdragon import route_handler
from swampdragon.route_handler import ModelPubRouter
from .models import NotificationUser
from .serializers import NotificationUserSerializer
from swampdragon.permissions import RoutePermission


class LoginRequired(RoutePermission):
    def __init__(self, verbs=None):
        self.test_against_verbs = verbs

    def test_permission(self, handler, verb, **kwargs):
        if 'user' not in kwargs and 'u_stream' not in kwargs['user']:
            return False

        return handler.connection.authenticate(kwargs['user']['u_stream'])

    def permission_failed(self, handler):
        handler.send_login_required()


class NotificationRouter(ModelPubRouter):
    permission_classes = [LoginRequired()]

    valid_verbs = ['subscribe']
    route_name = 'notifications'
    model = NotificationUser
    serializer_class = NotificationUserSerializer

    def get_subscription_contexts(self, **kwargs):
        user_obj = self.connection.get_user(kwargs['user']['u_stream'])

        if user_obj is None:
            return self.send_login_required()

        return {'user_id': user_obj.pk}

route_handler.register(NotificationRouter)
