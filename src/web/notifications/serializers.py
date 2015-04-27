from swampdragon.serializers.model_serializer import ModelSerializer


class NotificationUserSerializer(ModelSerializer):
    class Meta:
        model = 'notifications.NotificationUser'
        publish_fields = ['message']


class NotificationTeamSerializer(ModelSerializer):
    class Meta:
        model = 'notifications.NotificationTeam'
        publish_fields = ['message']
