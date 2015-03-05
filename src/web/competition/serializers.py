from competition.models import *
from groups.serializers import *


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = ('name', 'type_of_competition', 'enrolled_groups')
        read_only_fields = ('enrolled_groups',)


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
        fields = ('simulation_identifier', 'agent_name', 'round_name',)
        read_only_fields = ()

"""
---------------------------------------------------------------
APAGAR A PARTE DA SIMULATION QUANDO AS RONDAS ESTIVEREM PRONTAS
---------------------------------------------------------------
"""


class SimulationXSerializer(serializers.BaseSerializer):
    """
    This serializer is only to retrieve and list methods.
    """

    def to_representation(self, instance):
        return {
            'param_list_path': "media/tmp_simulations/Param.xml",
            'grid_path': "media/tmp_simulations/Ciber2010_Grid.xml",
            'lab_path': "media/tmp_simulations/Ciber2010_Lab.xml",
            'agent_path': "media/tmp_simulations/myrob.py"
        }
