from django.db import models
from swampdragon.models import SelfPublishModel
from .serializers import NotificationUserSerializer
from authentication.models import Account


class NotificationUser(SelfPublishModel, models.Model):
    serializer_class = NotificationUserSerializer
    message = models.TextField()
    user = models.ForeignKey(Account)