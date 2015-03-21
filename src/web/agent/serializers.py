from rest_framework import serializers
from authentication.serializers import AccountSerializer
from competition.serializers import RoundSerializer, CompetitionSerializer
from .models import Agent


class AgentSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(max_length=128)
    user = AccountSerializer(read_only=True)
    rounds = RoundSerializer(many=True, read_only=True)
    competitions = CompetitionSerializer(many=True, read_only=True)

    class Meta:
        model = Agent
        fields = ('agent_name', 'is_virtual', 'language', 'rounds', 'competitions', 'user', 'group_name', 'created_at',
                  'updated_at')
        read_only_fields = ('user', 'language', 'rounds', 'competitions', 'created_at', 'updated_at',)


class FileAgentSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'file': instance.file,
            'url': instance.url
        }