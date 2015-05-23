from django.db import models
from swampdragon.models import SelfPublishModel
from .serializers import NotificationUserSerializer, NotificationTeamSerializer, NotificationMessage, NotificationBroadcastSerializer
from authentication.models import Account, Team
from django.conf import settings
from competition.models import Trial


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
        message = handling_message(status, message, trigger)

        if channel != "admin":
            NotificationBroadcast.objects.create(broadcast=0, message=message)
            OldBroadcastNotification.sync(message=message)

        NotificationBroadcast.objects.create(broadcast=1, message=message)
        OldAdminNotification.sync(message=message)


class NotificationUser(SelfPublishModel, models.Model):
    serializer_class = NotificationUserSerializer
    message = models.TextField()
    user = models.ForeignKey(Account)

    @staticmethod
    def add(user, status, message, trigger=""):
        message = handling_message(status, message, trigger)
        NotificationUser.objects.create(user=user, message=message)
        OldNotificationUser.sync(user=user, message=message)


class NotificationTeam(SelfPublishModel, models.Model):
    serializer_class = NotificationTeamSerializer
    message = models.TextField()
    team = models.ForeignKey(Team)

    @staticmethod
    def add(team, status, message, trigger=""):
        message = handling_message(status, message, trigger)
        NotificationTeam.objects.create(team=team, message=message)
        OldNotificationTeam.sync(message=message, team=team)


class StreamTrial(SelfPublishModel, models.Model):
    serializer_class = StreamTrialSerializer
    message = models.TextField()
    trial = models.ForeignKey(Trial)

    @staticmethod
    def add(trial_identifier, message):
        trial = Trial.objects.get(identifier=trial_identifier)
        StreamTrial.objects.create(trial=trial, message=message)

# Old notifications


class OldAdminNotification(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def sync(message):
        # clean old admin notifications
        old = OldAdminNotification.objects.order_by('created_at').all()

        # create a new message
        OldAdminNotification.objects.create(message=message)

        if len(old) > settings.NUMBER_OF_NOTIFICATIONS_TO_SAVE:
            for notification in old[0:len(old)-settings.NUMBER_OF_NOTIFICATIONS_TO_SAVE]:
                notification.delete()


class OldBroadcastNotification(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def sync(message):
        # clean old notifications
        old = OldBroadcastNotification.objects.order_by('created_at').all()

        # create a new message
        OldBroadcastNotification.objects.create(message=message)

        if len(old) > settings.NUMBER_OF_NOTIFICATIONS_TO_SAVE:
            for notification in old[0:len(old) - settings.NUMBER_OF_NOTIFICATIONS_TO_SAVE]:
                notification.delete()


class OldNotificationUser(models.Model):
    message = models.TextField()
    user = models.ForeignKey(Account)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def sync(message, user):
        # clean old notifications
        old = OldNotificationUser.objects.order_by('created_at').filter(user=user)

        # create a new message
        OldNotificationUser.objects.create(message=message, user=user)

        if len(old) > settings.NUMBER_OF_NOTIFICATIONS_TO_SAVE:
            for notification in old[0:len(old) - settings.NUMBER_OF_NOTIFICATIONS_TO_SAVE]:
                notification.delete()


class OldNotificationTeam(models.Model):
    message = models.TextField()
    team = models.ForeignKey(Team)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def sync(message, team):
        # clean old notifications
        old = OldNotificationTeam.objects.order_by('created_at').filter(team=team)

        # create a new message
        OldNotificationTeam.objects.create(message=message, team=team)

        if len(old) > settings.NUMBER_OF_NOTIFICATIONS_TO_SAVE:
            for notification in old[0:len(old) - settings.NUMBER_OF_NOTIFICATIONS_TO_SAVE]:
                notification.delete()