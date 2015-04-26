from swampdragon import route_handler
from swampdragon.route_handler import ModelPubRouter
from .models import Notification
from .serializers import NotificationSerializer


class NotificationRouter(ModelPubRouter):
    """
    def get_subscription_channels(self, **kwargs):
        pass
    """
    valid_verbs = ['subscribe']
    route_name = 'notifications'
    model = Notification
    serializer_class = NotificationSerializer

"""
@login_required
def subscribe(self, **kwargs):
    super().subscribe(**kwargs)

def get_subscription_contexts(self, **kwargs):
    return {'user_id': self.connection.user.pk}
"""

route_handler.register(NotificationRouter)
