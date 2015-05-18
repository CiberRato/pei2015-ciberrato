from django.db import models
from swampdragon.models import SelfPublishModel
from .serializers import NotificationUserSerializer, NotificationTeamSerializer, NotificationMessage, NotificationBroadcastSerializer
from authentication.models import Account, Team


def handling_message(status, content, trigger):
    class Message:
        def __init__(self, s, c, t):
            self.status = s
            self.content = c
            self.trigger = t

    serializer = NotificationMessage(Message(status, content, trigger))
    return serializer.data


class NotificationBroadcast(SelfPublishModel, models.Model):
    serializer_class = NotificationBroadcastSerializer
    message = models.TextField()
    broadcast = models.IntegerField()

    @staticmethod
    def add(channel, status, message, trigger=""):
        if channel == "admin":
            NotificationBroadcast.objects.create(broadcast=1, message=handling_message(status, message, trigger))
        else:
            NotificationBroadcast.objects.create(broadcast=0, message=handling_message(status, message, trigger))
            NotificationBroadcast.objects.create(broadcast=1, message=handling_message(status, message, trigger))


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


class OldAdminNotification(models.Model):
    message = models.TextField()


class OldBroadcastNotification(models.Model):
    message = models.TextField()


class OldNoficationUser(models.Model):
    message = models.TextField()
    user = models.ForeignKey(Account)


class OldNotificationTeam(models.Model):
    message = models.TextField()
    team = models.ForeignKey(Team)