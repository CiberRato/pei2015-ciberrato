from swampdragon.serializers.model_serializer import ModelSerializer


class NotificationUserSerializer(ModelSerializer):
    class Meta:
        model = 'notifications.NotificationUser'
        publish_fields = ['message']
