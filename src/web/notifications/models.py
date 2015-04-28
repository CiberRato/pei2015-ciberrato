from django.db import models
from swampdragon.models import SelfPublishModel
from .serializers import NotificationUserSerializer, NotificationTeamSerializer, NotificationMessage
from authentication.models import Account, Team


def handling_message(status, content, trigger):
    class Message:
        def __init__(self, s, c, t):
            self.status = s
            self.content = c
            self.trigger = t

    serializer = NotificationMessage(Message(status, content, trigger))
    return serializer.data


class NotificationUser(SelfPublishModel, models.Model):
    serializer_class = NotificationUserSerializer
    message = models.TextField()
    user = models.ForeignKey(Account)

    @staticmethod
    def add(user, status, message, trigger=""):
        NotificationUser.objects.create(user=user, message=handling_message(status, message, trigger))


class NotificationTeam(SelfPublishModel, models.Model):
    serializer_class = NotificationTeamSerializer
    message = models.TextField()
    team = models.ForeignKey(Team)

    @staticmethod
    def add(team, status, message, trigger=""):
        NotificationTeam.objects.create(team=team, message=handling_message(status, message, trigger))