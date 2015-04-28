from swampdragon.connections.sockjs_connection import DjangoSubscriberConnection
from tokens.models import UserToken


class _RequestWrapper(object):
    def __init__(self, session):
        self.session = session


class HttpDataConnection(DjangoSubscriberConnection):

    def __init__(self, session):
        self._user = None
        super(HttpDataConnection, self).__init__(session)

    @staticmethod
    def get_user(token):
        try:
            exists = UserToken.objects.filter(key=token).count()
            if exists:
                return UserToken.objects.get(key=token).user
            return None
        except UserToken.DoesNotExist:
            return None

    @staticmethod
    def authenticate(token):
        try:
            exists = UserToken.objects.filter(key=token).count()
            return exists == 1
        except UserToken.DoesNotExist:
            return False
