import uuid

from django.core.validators import MinValueValidator, MinLengthValidator
from ciberonline.validators import validate_word
from django.db import models
from django.conf import settings
from authentication.models import Account, Team


class Competition(models.Model):
    name = models.CharField(max_length=128, blank=False, unique=True, validators=[validate_word, MinLengthValidator(1)])

    REGISTER = 'Register'
    COMPETITION = 'Competition'
    PAST = 'Past'

    STATE = (
        (REGISTER, 'Register'),
        (COMPETITION, 'Competition'),
        (PAST, 'Past'),
    )

    enrolled_teams = models.ManyToManyField(Team, through='TeamEnrolled', related_name="competition")

    allow_remote_agents = models.BooleanField(default=False)

    type_of_competition = models.ForeignKey('TypeOfCompetition', blank=False)
    state_of_competition = models.CharField(choices=STATE, default='Register', max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __unicode__(self):
        return self.name


class TypeOfCompetition(models.Model):
    name = models.CharField(max_length=128, blank=False, unique=True, validators=[validate_word, MinLengthValidator(1)])
    number_teams_for_trial = models.IntegerField(validators=[MinValueValidator(1)], blank=False, default=1)
    number_agents_by_grid = models.IntegerField(validators=[MinValueValidator(1)], blank=False, default=1)

    single_position = models.BooleanField(default=False)
    timeout = models.IntegerField(validators=[MinValueValidator(0)], default=5)

    class Meta:
        unique_together = ('name', 'number_teams_for_trial', 'number_agents_by_grid',)

    def __unicode__(self):
        return self.name


class TeamEnrolled(models.Model):
    competition = models.ForeignKey(Competition, blank=False)
    team = models.ForeignKey(Team, blank=False)

    valid = models.BooleanField(default=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('competition', 'team',)
        ordering = ['created_at']

    def __unicode__(self):
        return self.team.name


class Round(models.Model):
    name = models.CharField(max_length=128, blank=False, unique=True, validators=[validate_word, MinLengthValidator(1)])

    parent_competition = models.ForeignKey(Competition, blank=False)

    param_list_path = models.FileField(upload_to="params/%Y/%m/%d")
    grid_path = models.FileField(upload_to="grids/%Y/%m/%d")
    lab_path = models.FileField(upload_to="labs/%Y/%m/%d")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        get_latest_by = "created_at"

    def __unicode__(self):
        return self.name


class Agent(models.Model):
    agent_name = models.CharField(max_length=128, blank=False, validators=[validate_word, MinLengthValidator(1)])
    user = models.ForeignKey(Account, blank=False)
    team = models.ForeignKey(Team, blank=False)

    language = models.CharField(choices=settings.ALLOWED_UPLOAD_LANGUAGES+(('Unknown', 'Unknown'),), max_length=100, default="Python")

    code_valid = models.BooleanField(default=False)
    validation_result = models.CharField(max_length=512)

    is_remote = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        unique_together = ('team', 'agent_name',)

    def __unicode__(self):
        return self.agent_name


class AgentFile(models.Model):
    agent = models.ForeignKey(Agent, blank=False)
    file = models.FileField(upload_to="agents/%Y/%m/%d")
    original_name = models.CharField(max_length=128, blank=False)

    class Meta:
        unique_together = ('agent', 'original_name',)


class GridPositions(models.Model):
    identifier = models.CharField(max_length=100, blank=False, unique=True, default=uuid.uuid4)
    competition = models.ForeignKey(Competition, blank=False)
    team = models.ForeignKey(Team, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('competition', 'team',)

    def __unicode__(self):
        return self.identifier


class AgentGrid(models.Model):
    agent = models.ForeignKey(Agent, blank=False)
    position = models.IntegerField(validators=[MinValueValidator(1)], blank=False)
    grid_position = models.ForeignKey(GridPositions, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('position', 'grid_position',)
        ordering = ('position', 'grid_position',)


class CompetitionAgent(models.Model):
    competition = models.ForeignKey(Competition, blank=False)
    round = models.ForeignKey(Round, blank=False)
    agent = models.ForeignKey(Agent, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('competition', 'round', 'agent',)
        ordering = ['created_at']


class LogTrialAgent(models.Model):
    competition_agent = models.ForeignKey('CompetitionAgent')
    trial = models.ForeignKey('Trial')

    pos = models.IntegerField(blank=False)

    class Meta:
        unique_together = ('pos', 'trial',)


class Trial(models.Model):
    identifier = models.CharField(max_length=100, blank=False, unique=True, default=uuid.uuid4)

    round = models.ForeignKey(Round, blank=False)

    started = models.BooleanField(default=False)
    waiting = models.BooleanField(default=False)
    errors = models.CharField(max_length=150)

    log_json = models.FileField(upload_to="json_logs/%Y/%m/%d")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        get_latest_by = "created_at"

    def __unicode__(self):
        return self.identifier


class TrialGrid(models.Model):
    grid_positions = models.ForeignKey(GridPositions, blank=False)
    trial = models.ForeignKey(Trial, blank=False)
    position = models.IntegerField(validators=[MinValueValidator(1)], blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('position', 'trial',)
        ordering = ('position', 'grid_positions', 'trial')


class TeamScore(models.Model):
    trial = models.ForeignKey(Trial, blank=False)
    team = models.ForeignKey(Team, blank=False)
    score = models.IntegerField(validators=[MinValueValidator(0)], blank=False)
    number_of_agents = models.IntegerField(validators=[MinValueValidator(0)], blank=False)
    time = models.IntegerField(validators=[MinValueValidator(0)], blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('trial', 'team',)
        ordering = ('score', '-number_of_agents', 'time')
