from swampdragon.connections.sockjs_connection import DjangoSubscriberConnection


class _RequestWrapper(object):
    def __init__(self, session):
        self.session = session


class HttpDataConnection(DjangoSubscriberConnection):

    def __init__(self, session):
        self._user = None
        super(HttpDataConnection, self).__init__(session)

    def get_user(self, token):
        from rest_framework.authtoken.models import Token

        try:
            exists = Token.objects.filter(key=token).count()
            if exists:
                return Token.objects.get(key=token).user
            return None
        except Token.DoesNotExist:
            return None

    def authenticate(self, token):
        from rest_framework.authtoken.models import Token
        try:
            exists = Token.objects.filter(key=token).count()
            return exists == 1
        except Token.DoesNotExist:
            return False
