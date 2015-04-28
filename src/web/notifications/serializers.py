from swampdragon.serializers.model_serializer import ModelSerializer
from rest_framework.serializers import BaseSerializer


class NotificationUserSerializer(ModelSerializer):
    class Meta:
        model = 'notifications.NotificationUser'
        publish_fields = ['message']


class NotificationTeamSerializer(ModelSerializer):
    class Meta:
        model = 'notifications.NotificationTeam'
        publish_fields = ['message']


class NotificationBroadcastSerializer(ModelSerializer):
    class Meta:
        model = 'notifications.NotificationBroadcast'
        publish_fields = ['message']


class NotificationMessage(BaseSerializer):

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def to_internal_value(self, data):
        pass

    def to_representation(self, instance):
        if instance.status == "error":
            status = 400
        else:
            status = 200

        return {
            'status': status,
            'content': instance.content,
            'trigger': instance.trigger
        }