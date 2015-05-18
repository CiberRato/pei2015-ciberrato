from rest_framework.serializers import ModelSerializer, BaseSerializer
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


class OldNotificationUserSerializer(ModelSerializer):

    class Meta:
        model = OldNotificationUser
        fields = ('message', 'user', 'created_at',)
        read_only_fields = ('message', 'user', 'created_at',)


class OldNotificationTeamSerializer(ModelSerializer):

    class Meta:
        model = OldNotificationTeam
        fields = ('message', 'team', 'created_at',)
        read_only_fields = ('message', 'team', 'created_at',)


class OldNotificationByTeamSerializer(BaseSerializer):

    def to_representation(self, instance):
        notifications = OldNotificationTeamSerializer(instance.notifications)

        return {
            'team': instance.team,
            'notifications': notifications.data
        }