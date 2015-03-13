from competition.models import *
from groups.serializers import *


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = ('name', 'type_of_competition', 'state_of_competition')
        read_only_fields = ('state_of_competition',)


class RoundSerializer(serializers.ModelSerializer):
    parent_competition_name = serializers.CharField(max_length=128)

    class Meta:
        model = Round
        fields = ('name', 'parent_competition_name', 'param_list_path', 'grid_path', 'lab_path', 'agents_list')
        read_only_fields = ('param_list_path', 'grid_path', 'lab_path', 'agents_list',)


class GroupEnrolledSerializer(serializers.ModelSerializer):
    competition_name = serializers.CharField(max_length=128)
    group_name = serializers.CharField(max_length=128)

    class Meta:
        model = GroupEnrolled
        fields = ('competition_name', 'group_name',)


class AgentSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(max_length=128)
    user = AccountSerializer(read_only=True)
    rounds = RoundSerializer(many=True)
    competitions = CompetitionSerializer(many=True)

    class Meta:
        model = Agent
        fields = ('agent_name', 'is_virtual', 'language', 'rounds', 'competitions', 'user', 'group_name', 'created_at',
                  'updated_at')
        read_only_fields = ('user', 'language', 'rounds', 'competitions', 'created_at', 'updated_at',)


class CompetitionAgentSerializer(serializers.ModelSerializer):
    round_name = serializers.CharField(max_length=128)
    agent_name = serializers.CharField(max_length=128)

    class Meta:
        model = CompetitionAgent
        fields = ('round_name', 'agent_name', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at',)


class SimulationSerializer(serializers.ModelSerializer):
    round_name = serializers.CharField(max_length=128)

    class Meta:
        model = Simulation
        fields = ('identifier', 'round_name', 'created_at', 'updated_at',)
        read_only_fields = ('identifier', 'created_at', 'updated_at',)


class SimulationAgentSerializer(serializers.ModelSerializer):
    simulation_identifier = serializers.CharField(max_length=100)
    agent_name = serializers.CharField(max_length=128)
    round_name = serializers.CharField(max_length=128)

    class Meta:
        model = LogSimulationAgent
        fields = ('simulation_identifier', 'agent_name', 'round_name', 'pos',)
        read_only_fields = ()


class LogSimulation(serializers.ModelSerializer):
    simulation_identifier = serializers.CharField(max_length=100)

    class Meta:
        model = Simulation
        fields = ('simulation_identifier', 'log_json', 'simulation_log_xml',)
        read_only_fields = ()


class AgentXSerializer(serializers.BaseSerializer):

    def to_representation(self, instance):
        if not instance.files:
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


class SimulationXSerializer(serializers.BaseSerializer):

    def to_representation(self, instance):
        agents = AgentXSerializer(instance.agents, many=True)
        return {
            'simulation_id': instance.simulation_id,
            'grid': instance.grid,
            'param_list': instance.param_list,
            'lab': instance.lab,
            'agents': agents.data
        }
