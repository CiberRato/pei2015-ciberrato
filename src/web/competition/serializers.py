from django.core.files.storage import default_storage
from os.path import basename

from rest_framework import serializers
from rest_framework.validators import ValidationError

from competition.models import Competition, Round, TeamEnrolled, CompetitionAgent, Trial, LogTrialAgent, \
    TypeOfCompetition, GridPositions, AgentGrid, TrialGrid, TeamScore, AgentScoreRound
from teams.serializers import TeamSerializer


class TypeOfCompetitionSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = TypeOfCompetition
        fields = ('name', 'number_teams_for_trial', 'number_agents_by_grid', 'allow_remote_agents',
                  'synchronous_simulation', 'single_position', 'timeout')
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
    competition_name = serializers.CharField(max_length=128)
    state = serializers.CharField(max_length=128, read_only=True)

    class Meta:
        model = Trial
        fields = ('identifier', 'round_name', 'competition_name', 'state', 'errors', 'created_at', 'updated_at',)
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


class AutomaticTeamScoreHallOfFameSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(write_only=True)
    trial_id = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = AgentScoreRound
        fields = ('trial_id', 'score', 'number_of_agents', 'time',)
        read_only_fields = ()


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


class TrialMessageSerializer(serializers.BaseSerializer):
    def to_internal_value(self, data):
        trial_identifier = data.get('trial_identifier')
        message = data.get('message')

        # Perform the data validation.
        if not message:
            raise ValidationError({
                'message': 'This field is required.'
            })
        if not trial_identifier:
            raise ValidationError({
                'trial_identifier': 'This field is required.'
            })

        # Return the validated values. This will be available as
        # the `.validated_data` property.
        return {
            'message': message,
            'trial_identifier': trial_identifier
        }


class AgentXSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        if not hasattr(instance, "files"):
            return {
                'agent_type': instance.agent_type,
                'agent_name': instance.agent_name,
                'team_name': instance.team_name,
                'pos': instance.pos,
                'language': instance.language
            }
        else:
            return {
                'agent_type': instance.agent_type,
                'agent_name': instance.agent_name,
                'team_name': instance.team_name,
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


class FolderSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'type': 'folder',
            'name': instance.name,
            'sub': instance.sub
        }


class RFileSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'type': 'file',
            'name': instance.name,
            'path': instance.path
        }


class PrivateCompetitionSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        competition = CompetitionSerializer(instance.competition)
        rounds = Round.objects.filter(parent_competition=instance.competition)
        trials = reduce(lambda r, h: r + h.trial_set.count(), rounds.all(), 0)

        return {
            'competition': competition.data,
            'team': instance.team.name,
            'number_of_rounds': rounds.count(),
            'number_of_trials': trials
        }


class PrivateRoundSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        grid = basename(default_storage.path(instance.grid_path))
        lab = basename(default_storage.path(instance.lab_path))
        param_list = basename(default_storage.path(instance.param_list_path))

        return {
            'name': instance.name,
            'grid': grid,
            'grid_path': "resources/"+default_storage.path(instance.grid_path).split('/media/resources/')[1],
            'param_list': param_list,
            'lab': lab,
            'lab_path': "resources/" + default_storage.path(instance.lab_path).split('/media/resources/')[1],
            'created_at': instance.created_at,
            'updated_at': instance.updated_at
        }


class PrivateRoundTrialsSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'round': instance.round,
            'trials': instance.trials
        }


class InputPrivateRoundSerializer(serializers.ModelSerializer):
    competition_name = serializers.CharField(max_length=128)
    grid = serializers.CharField(max_length=150)
    param_list = serializers.CharField(max_length=150)
    lab = serializers.CharField(max_length=150)

    class Meta:
        model = Round
        fields = ('competition_name', 'grid', 'param_list', 'lab',)
        read_only_fields = ()


class ExecutionLogSerializer(serializers.ModelSerializer):
    trial_id = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = Trial
        fields = ('trial_id', 'execution_log',)
        read_only_fields = ()


class HallOfFameLaunchSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        pass

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def to_internal_value(self, data):
        round_name = data.get('round_name')
        agent_name = data.get('agent_name')
        team_name = data.get('team_name')

        # Perform the data validation.
        if not round_name:
            raise ValidationError({
                'message': 'This field is required.'
            })
        if not agent_name:
            raise ValidationError({
                'message': 'This field is required.'
            })
        if not team_name:
            raise ValidationError({
                'message': 'This field is required.'
            })

        # Return the validated values. This will be available as
        # the `.validated_data` property.
        return {
            'round_name': round_name,
            'team_name': team_name,
            'agent_name': agent_name
        }


class HallOfFameSerializer(serializers.BaseSerializer):

    def to_representation(self, instance):
        return {
            'team_name': instance.team.name,
            'round_name': instance.round.name,
            'trial_identifier': instance.trial.identifier,
            'score': instance.score,
            'number_of_agents': instance.number_of_agents,
            'time': instance.time
        }