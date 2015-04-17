from rest_framework import serializers

from competition.models import Competition, Round, GroupEnrolled, CompetitionAgent, Simulation, LogSimulationAgent,\
    TypeOfCompetition, GridPositions, AgentGrid, SimulationGrid
from groups.serializers import GroupSerializer


class TypeOfCompetitionSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = TypeOfCompetition
        fields = ('name', 'number_teams_for_trial', 'number_agents_by_grid')
        read_only_fields = ()


class AgentGridSerializer(serializers.ModelSerializer):
    grid_identifier = serializers.CharField()
    agent_name = serializers.CharField()

    class Meta:
        model = AgentGrid
        fields = ('grid_identifier', 'agent_name', 'position')
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


class GridPositionsSerializer(serializers.ModelSerializer):
    competition_name = serializers.CharField(write_only=True)
    group_name = serializers.CharField()

    competition = CompetitionSerializer(read_only=True)

    class Meta:
        model = GridPositions
        fields = ('identifier', 'competition',  'competition_name', 'group_name')
        read_only_fields = ('competition', 'identifier',)


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
    competition_name = serializers.CharField(max_length=128, write_only=True)
    group_name = serializers.CharField(max_length=128)
    valid = serializers.BooleanField(read_only=True)


    competition = CompetitionSerializer(read_only=True)

    class Meta:
        model = GroupEnrolled
        fields = ('competition', 'competition_name', 'group_name', 'valid',)
        read_only_fields = ('competition', 'valid',)


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


class SimulationGridsSerializer(serializers.ModelSerializer):
    grid_positions = GridPositionsSerializer()

    class Meta:
        model = SimulationGrid
        fields = ('grid_positions', 'position')
        read_only_fields = ()


class SimulationGridInputSerializer(serializers.ModelSerializer):
    simulation_identifier = serializers.CharField(max_length=128)
    grid_identifier = serializers.CharField(max_length=128)

    class Meta:
        model = SimulationGrid
        fields = ('simulation_identifier', 'grid_identifier', 'position')
        read_only_fields = ()


class SimulationAgentSerializer(serializers.ModelSerializer):
    simulation_identifier = serializers.CharField(max_length=100)
    agent_name = serializers.CharField(max_length=128)
    round_name = serializers.CharField(max_length=128)

    class Meta:
        model = LogSimulationAgent
        fields = ('simulation_identifier', 'agent_name', 'round_name', 'pos',)
        read_only_fields = ()


class RoundFileSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'file': instance.file,
            'last_modification': instance.last_modification,
            'size': instance.size,
            'url': instance.url
        }


class RoundFilesSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        param = RoundFileSerializer(instance.param_list)
        grid = RoundFileSerializer(instance.grid)
        lab = RoundFileSerializer(instance.lab)

        return {
            'param_list': param.data,
            'grid': grid.data,
            'lab': lab.data
        }