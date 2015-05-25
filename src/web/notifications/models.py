from django.db import models
from .serializers import NotificationUserSerializer, NotificationTeamSerializer, NotificationMessage, \
    NotificationBroadcastSerializer, StreamTrialSerializer
from authentication.models import Account, Team
from django.conf import settings
from competition.models import Trial
from django.db.models import ForeignKey
from swampdragon.pubsub_providers.base_provider import PUBACTIONS
from swampdragon.model_tools import get_property
from swampdragon.pubsub_providers.model_publisher import publish_model
from swampdragon.serializers.serializer_importer import get_serializer
from django.db.models.signals import m2m_changed
from django.dispatch.dispatcher import receiver


class SelfPublishModel(object):
    serializer_class = None

    def __init__(self, *args, **kwargs):
        if isinstance(self.serializer_class, str):
            self.serializer_class = get_serializer(self.serializer_class, self)
        self._pre_save_state = dict()
        super(SelfPublishModel, self).__init__(*args, **kwargs)
        self._serializer = self.serializer_class(instance=self)
        self._set_pre_save_state()

    def _set_pre_save_state(self):
        """
        Set the state of the model before any changes are done,
        so it's possible to determine what fields have changed.
        """
        relevant_fields = self._get_relevant_fields()
        for field in relevant_fields:
            val = get_property(self, field)
            if hasattr(self._serializer, field):
                continue
            if val is None:
                self._pre_save_state[field] = None
                continue
            self._pre_save_state[field] = val

    def _get_relevant_fields(self):
        """
        Get all fields that will affect the state.
        This is used to save the state of the model before it's updated,
        to be able to get changes used when publishing an update (so not all fields are published)
        """
        relevant_fields = self._serializer.base_fields

        if 'id' in relevant_fields:
            relevant_fields.remove('id')

        relevant_fields_copy = []

        # check for any foreign keys and include the key to the object instead of the object itself
        # This is to avoid triggering queries to retrieve the foreign object
        for field in self._meta.fields:
            if field.name in relevant_fields:
                if type(field) in (ForeignKey, ):
                    # typically field.attname is field.name + "_id" ie field_id
                    relevant_fields_copy.append(field.attname)
                else:
                    relevant_fields_copy.append(field.name)

        return relevant_fields_copy

        # for field_name in relevant_fields:
        #     field = self._meta.get_field_by_name(field_name)[0]
        #     if isinstance(field, ForeignKey):
        #         relevant_fields.remove(field_name)
        #
        # return relevant_fields

    def get_changed_fields(self):
        changed_fields = []
        for k, v in self._pre_save_state.items():
            val = get_property(self, k)
            if val != v:
                changed_fields.append(k)
        return changed_fields

    def serialize(self):
        return self._serializer.serialize()

    def _publish(self, action, changed_fields=None):
        publish_model(self, self._serializer, action, changed_fields)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.action = PUBACTIONS.created
            self.changed_fields = None
        else:
            self.action = PUBACTIONS.updated
            self.changed_fields = self.get_changed_fields()
        super(SelfPublishModel, self).save(*args, **kwargs)
        self._publish(self.action, self.changed_fields)

        # Set the pre-save state to the current state
        # in case the model is changed again before retrieval
        self._set_pre_save_state()


@receiver(m2m_changed)
def _self_publish_model_m2m_change(sender, instance, action, model, pk_set, **kwargs):
    if not isinstance(instance, SelfPublishModel):
        return
    instance.action = PUBACTIONS.updated
    if action in ['post_add', 'post_clear', 'post_remove']:
        instance._publish(instance.action, instance._serializer.opts.publish_fields)


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