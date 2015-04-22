import datetime

from rest_framework import serializers
from authentication.serializers import AccountSerializer
from competition.serializers import RoundSerializer, CompetitionSerializer
from .models import Agent


class AgentSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(max_length=128)
    user = AccountSerializer(read_only=True)
    rounds = RoundSerializer(many=True, read_only=True)
    competitions = CompetitionSerializer(many=True, read_only=True)

    class Meta:
        model = Agent
        fields = ('agent_name', 'is_local', 'rounds', 'code_valid', 'validation_result', 'language', 'competitions', 'user', 'team_name', 'created_at',
                  'updated_at')
        read_only_fields = ('user', 'rounds', 'code_valid', 'validation_result', 'competitions', 'created_at', 'updated_at',)


class SubmitCodeAgentSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(max_length=128)

    class Meta:
        model = Agent
        fields = ('agent_name',)
        read_only_fields = ()


class AgentCodeValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ('code_valid', 'validation_result',)
        read_only_fields = ()


class FileAgentSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'file': instance.file,
            'url': instance.url,
            'last_modification': datetime.datetime.fromtimestamp(
                int(instance.last_modification)
            ).strftime('%Y-%m-%d %H:%M:%S'),
            'size': instance.size
        }


class LanguagesSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'name': instance.name,
            'value': instance.value
        }