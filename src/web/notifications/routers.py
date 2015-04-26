from swampdragon import route_handler
from swampdragon.route_handler import ModelPubRouter
from .models import Notification
from .serializers import NotificationSerializer
from swampdragon.permissions import RoutePermission


class LoginRequired(RoutePermission):
    def __init__(self, verbs=None):
        self.test_against_verbs = verbs

    def test_permission(self, handler, verb, **kwargs):
        if 'user' not in kwargs and 'stream' not in kwargs['user']:
            return False

        return handler.connection.authenticate(kwargs['user']['stream'])

    def permission_failed(self, handler):
        handler.send_login_required()


class NotificationRouter(ModelPubRouter):
    permission_classes = [LoginRequired()]

    valid_verbs = ['subscribe']
    route_name = 'notifications'
    model = Notification
    serializer_class = NotificationSerializer

    def get_subscription_contexts(self, **kwargs):
        user_obj = self.connection.get_user(kwargs['user']['stream'])

        if user_obj is None:
            return self.send_login_required()

        return {'user_id': user_obj.pk}

route_handler.register(NotificationRouter)
