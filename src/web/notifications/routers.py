from swampdragon import route_handler
from swampdragon.route_handler import ModelPubRouter
from .models import Notification
from .serializers import NotificationSerializer
from swampdragon.permissions import RoutePermission
from authentication.models import Account


class LoginRequired(RoutePermission):
    def __init__(self, verbs=None):
        self.test_against_verbs = verbs

    def test_permission(self, handler, verb, **kwargs):
        if 'user' not in kwargs:
            return False

        user = kwargs['user']

        if self.test_against_verbs is not None:
            if verb not in self.test_against_verbs:
                return False
        return user is not None

    def permission_failed(self, handler):
        handler.send_login_required()


class NotificationRouter(ModelPubRouter):
    permission_classes = [LoginRequired()]

    valid_verbs = ['subscribe']
    route_name = 'notifications'
    model = Notification
    serializer_class = NotificationSerializer

    def get_subscription_contexts(self, **kwargs):
        user_obj = Account.objects.get(username=kwargs['user']['username'])
        user = user_obj.pk
        return {'user_id': user}


route_handler.register(NotificationRouter)
