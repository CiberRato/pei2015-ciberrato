from django.db import models
from swampdragon.models import SelfPublishModel
from .serializers import NotificationUserSerializer, NotificationTeamSerializer
from authentication.models import Account, Team


class NotificationUser(SelfPublishModel, models.Model):
    serializer_class = NotificationUserSerializer
    message = models.TextField()
    user = models.ForeignKey(Account)


class NotificationTeam(SelfPublishModel, models.Model):
    serializer_class = NotificationTeamSerializer
    message = models.TextField()
    team = models.ForeignKey(Team)
