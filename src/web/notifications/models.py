from django.db import models
from swampdragon.models import SelfPublishModel
from .serializers import NotificationSerializer
# from authentication.models import Account


class Notification(SelfPublishModel, models.Model):
    serializer_class = NotificationSerializer
    message = models.TextField()
    # user = models.ForeignKey(Account)
