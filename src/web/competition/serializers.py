from rest_framework import serializers

from competition.models import Competition, Round, GroupEnrolled, CompetitionAgent, Simulation, LogSimulationAgent,\
    TypeOfCompetition, PolePosition, AgentPole
from groups.serializers import GroupSerializer


class TypeOfCompetitionSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    number_teams_for_trial = serializers.IntegerField()
    number_agents_by_grid = serializers.IntegerField()

    class Meta:
        model = TypeOfCompetition
        fields = ('name', 'number_teams_for_trial', 'number_agents_by_grid')
        read_only_fields = ()


class PolePositionSerializer(serializers.ModelSerializer):
    competition_name = serializers.CharField()
    group_name = serializers.CharField()

    class Meta:
        model = PolePosition
        fields = ('identifier', 'competition_name', 'group_name')
        read_only_fields = ('identifier',)


class AgentPoleSerializer(serializers.ModelSerializer):
    pole_identifier = serializers.CharField()
    agent_name = serializers.CharField()

    class Meta:
        model = AgentPole
        fields = ('pole_identifier', 'agent_name')
        read_only_fields = ()


class CompetitionSerializer(serializers.ModelSerializer):
    type_of_competition = TypeOfCompetitionSerializer()

    class Meta:
        model = Competition
        fields = ('name', 'type_of_competition', 'state_of_competition')
        read_only_fields = ('name', 'type_of_competition', 'state_of_competition')


class CompetitionInputSerializer(serializers.ModelSerializer):
    type_of_competition = serializers.CharField(max_length=128)

    class Meta:
        model = Competition
        fields = ('name', 'type_of_competition', 'state_of_competition')
        read_only_fields = ('state_of_competition',)


class CompetitionStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = ('state_of_competition',)
        read_only_fields = ()


class RoundSerializer(serializers.ModelSerializer):
    parent_competition_name = serializers.CharField(max_length=128)

    class Meta:
        model = Round
        fields = ('name', 'parent_competition_name',)
        read_only_fields = ()


class AdminRoundSerializer(serializers.ModelSerializer):
    parent_competition_name = serializers.CharField(max_length=128)

    class Meta:
        model = Round
        fields = ('name', 'parent_competition_name', 'param_list_path', 'grid_path', 'lab_path',)
        read_only_fields = ('param_list_path', 'grid_path', 'lab_path',)


class GroupEnrolledSerializer(serializers.ModelSerializer):
    competition_name = serializers.CharField(max_length=128)
    group_name = serializers.CharField(max_length=128)
    valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = GroupEnrolled
        fields = ('competition_name', 'group_name', 'valid',)
        read_only_fields = ('valid',)


class GroupEnrolledOutputSerializer(serializers.ModelSerializer):
    group = GroupSerializer(read_only=True)

    class Meta:
        model = GroupEnrolled
        fields = ('group', 'valid',)
        read_only_fields = ('group', 'valid')


class CompetitionAgentSerializer(serializers.ModelSerializer):
    competition_name = serializers.CharField(max_length=128)
    agent_name = serializers.CharField(max_length=128)

    class Meta:
        model = CompetitionAgent
        fields = ('competition_name', 'agent_name', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at',)


class RoundAgentSerializer(serializers.ModelSerializer):
    round_name = serializers.CharField(max_length=128)
    agent_name = serializers.CharField(max_length=128)

    class Meta:
        model = CompetitionAgent
        fields = ('round_name', 'agent_name', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at',)


class SimulationSerializer(serializers.ModelSerializer):
    round_name = serializers.CharField(max_length=128)
    state = serializers.CharField(max_length=128, read_only=True)

    class Meta:
        model = Simulation
        fields = ('identifier', 'round_name', 'state', 'created_at', 'updated_at',)
        read_only_fields = ('identifier', 'state', 'created_at', 'updated_at',)


class SimulationAgentSerializer(serializers.ModelSerializer):
    simulation_identifier = serializers.CharField(max_length=100)
    agent_name = serializers.CharField(max_length=128)
    round_name = serializers.CharField(max_length=128)

    class Meta:
        model = LogSimulationAgent
        fields = ('simulation_identifier', 'agent_name', 'round_name', 'pos',)
        read_only_fields = ()


class RoundFilesSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'param_list': {
                'name': instance.param_list[0],
                'size': instance.param_list[1]
            },
            'grid': {
                'name': instance.grid[0],
                'size': instance.grid[1]
            },
            'lab': {
                'name': instance.lab[0],
                'size': instance.lab[1]
            }
        }