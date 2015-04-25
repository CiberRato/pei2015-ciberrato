from rest_framework import serializers

from competition.models import Competition, Round, TeamEnrolled, CompetitionAgent, Trial, LogTrialAgent, \
    TypeOfCompetition, GridPositions, AgentGrid, TrialGrid, TeamScore
from teams.serializers import TeamSerializer


class TypeOfCompetitionSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = TypeOfCompetition
        fields = ('name', 'number_teams_for_trial', 'number_agents_by_grid', 'single_position', 'timeout')
        read_only_fields = ()


class AgentGridSerializer(serializers.ModelSerializer):
    grid_identifier = serializers.CharField()
    agent_name = serializers.CharField()
    team_name = serializers.CharField()

    class Meta:
        model = AgentGrid
        fields = ('grid_identifier', 'agent_name', 'team_name', 'position')
        read_only_fields = ()


class AgentRemoteGridSerializer(serializers.ModelSerializer):
    grid_identifier = serializers.CharField()

    class Meta:
        model = AgentGrid
        fields = ('grid_identifier', 'position')
        read_only_fields = ()


class CompetitionSerializer(serializers.ModelSerializer):
    type_of_competition = TypeOfCompetitionSerializer()

    class Meta:
        model = Competition
        fields = ('name', 'type_of_competition', 'state_of_competition', 'allow_remote_agents')
        read_only_fields = ('name', 'type_of_competition', 'state_of_competition', 'allow_remote_agents')


class CompetitionInputSerializer(serializers.ModelSerializer):
    type_of_competition = serializers.CharField(max_length=128)

    class Meta:
        model = Competition
        fields = ('name', 'type_of_competition', 'allow_remote_agents', 'state_of_competition')
        read_only_fields = ('state_of_competition',)


class GridPositionsSerializer(serializers.ModelSerializer):
    competition_name = serializers.CharField(write_only=True)
    team_name = serializers.CharField()

    competition = CompetitionSerializer(read_only=True)

    class Meta:
        model = GridPositions
        fields = ('identifier', 'competition', 'competition_name', 'team_name')
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


class TeamEnrolledSerializer(serializers.ModelSerializer):
    competition_name = serializers.CharField(max_length=128, write_only=True)
    team_name = serializers.CharField(max_length=128)
    valid = serializers.BooleanField(read_only=True)

    competition = CompetitionSerializer(read_only=True)

    class Meta:
        model = TeamEnrolled
        fields = ('competition', 'competition_name', 'team_name', 'valid',)
        read_only_fields = ('competition', 'valid',)


class TeamEnrolledOutputSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)

    class Meta:
        model = TeamEnrolled
        fields = ('team', 'valid',)
        read_only_fields = ('team', 'valid')


class CompetitionAgentSerializer(serializers.ModelSerializer):
    competition_name = serializers.CharField(max_length=128)
    agent_name = serializers.CharField(max_length=128)
    team_name = serializers.CharField(max_length=128)

    class Meta:
        model = CompetitionAgent
        fields = ('competition_name', 'agent_name', 'team_name', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at',)


class RoundAgentSerializer(serializers.ModelSerializer):
    round_name = serializers.CharField(max_length=128)
    agent_name = serializers.CharField(max_length=128)
    team_name = serializers.CharField(max_length=128)

    class Meta:
        model = CompetitionAgent
        fields = ('round_name', 'agent_name', 'team_name', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at',)


class TrialSerializer(serializers.ModelSerializer):
    round_name = serializers.CharField(max_length=128)
    state = serializers.CharField(max_length=128, read_only=True)

    class Meta:
        model = Trial
        fields = ('identifier', 'round_name', 'state', 'errors', 'created_at', 'updated_at',)
        read_only_fields = ('identifier', 'state', 'errors', 'created_at', 'updated_at',)


class TrialGridsSerializer(serializers.ModelSerializer):
    grid_positions = GridPositionsSerializer()

    class Meta:
        model = TrialGrid
        fields = ('grid_positions', 'position')
        read_only_fields = ()


class TrialGridInputSerializer(serializers.ModelSerializer):
    trial_identifier = serializers.CharField(max_length=128)
    grid_identifier = serializers.CharField(max_length=128)

    class Meta:
        model = TrialGrid
        fields = ('trial_identifier', 'grid_identifier', 'position')
        read_only_fields = ()


class TrialAgentSerializer(serializers.ModelSerializer):
    trial_identifier = serializers.CharField(max_length=100)
    agent_name = serializers.CharField(max_length=128)
    team_name = serializers.CharField(max_length=128)
    round_name = serializers.CharField(max_length=128)

    class Meta:
        model = LogTrialAgent
        fields = ('trial_identifier', 'agent_name', 'team_name', 'round_name', 'pos',)
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


class TeamScoreInSerializer(serializers.ModelSerializer):
    trial_id = serializers.CharField(max_length=128, write_only=True)
    team_name = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = TeamScore
        fields = ('trial_id', 'team_name', 'score', 'number_of_agents', 'time',)
        read_only_fields = ()


class TeamScoreOutSerializer(serializers.ModelSerializer):
    trial = TrialSerializer(read_only=True)
    team = TeamSerializer(read_only=True)

    class Meta:
        model = TeamScore
        fields = ('trial', 'team', 'score', 'number_of_agents', 'time',)
        read_only_fields = ('trial', 'team',)