from rest_framework import serializers
from .models import Trial
from competition.serializers import TypeOfCompetitionSerializer


class LogTrial(serializers.ModelSerializer):
    trial_identifier = serializers.CharField(max_length=100)

    class Meta:
        model = Trial
        fields = ('trial_identifier', 'log_json',)
        read_only_fields = ()


class ErrorTrial(serializers.ModelSerializer):
    trial_identifier = serializers.CharField(max_length=100)
    msg = serializers.CharField(max_length=150)

    class Meta:
        model = Trial
        fields = ('trial_identifier', 'msg',)
        read_only_fields = ()


class AgentXSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        if not hasattr(instance, "files"):
            return {
                'agent_type': instance.agent_type,
                'agent_name': instance.agent_name,
                'pos': instance.pos,
                'language': instance.language
            }
        else:
            return {
                'agent_type': instance.agent_type,
                'agent_name': instance.agent_name,
                'pos': instance.pos,
                'language': instance.language,
                'files': instance.files
            }


class TrialXSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        agents = AgentXSerializer(instance.agents, many=True)
        type_of_competition = TypeOfCompetitionSerializer(instance.type_of_competition)

        return {
            'trial_id': instance.trial_id,
            'grid': instance.grid,
            'param_list': instance.param_list,
            'lab': instance.lab,
            'type_of_competition': type_of_competition.data,
            'agents': agents.data
        }