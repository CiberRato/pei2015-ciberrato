from swampdragon import route_handler
from swampdragon.route_handler import ModelPubRouter
from .models import Notification
from .serializers import NotificationSerializer
from swampdragon.permissions import LoginRequired


class NotificationRouter(ModelPubRouter):
    # permission_classes = [LoginRequired()]

    valid_verbs = ['subscribe']
    route_name = 'notifications'
    model = Notification
    serializer_class = NotificationSerializer

    """
    def get_subscription_contexts(self, **kwargs):
        return {'user_id': self.connection.user.pk}
    """
"""
@login_required
def subscribe(self, **kwargs):
    super().subscribe(**kwargs)

def get_subscription_contexts(self, **kwargs):
    return {'user_id': self.connection.user.pk}
"""

route_handler.register(NotificationRouter)
