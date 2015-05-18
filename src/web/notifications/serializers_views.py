from swampdragon.serializers.model_serializer import ModelSerializer
from .models import OldAdminNotification, OldBroadcastNotification, OldNotificationUser, OldNotificationTeam


class OldAdminNotificationSerializer(ModelSerializer):

    class Meta:
        model = OldAdminNotification
        fields = ('message', 'created_at',)
        read_only_fields = ('message', 'created_at',)


class OldBroadcastNotificationSerializer(ModelSerializer):

    class Meta:
        model = OldBroadcastNotification
        fields = ('message', 'created_at',)
        read_only_fields = ('message', 'created_at',)
