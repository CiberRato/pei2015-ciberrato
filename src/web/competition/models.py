import uuid
from django.core.validators import validate_slug, MinValueValidator
from django.db import models
from django.conf import settings
from authentication.models import Account, Group


class Competition(models.Model):
    name = models.CharField(max_length=128, blank=False, unique=True, validators=[validate_slug])

    REGISTER = 'Register'
    COMPETITION = 'Competition'
    PAST = 'Past'

    STATE = (
        (REGISTER, 'Register'),
        (COMPETITION, 'Competition'),
        (PAST, 'Past'),
    )

    enrolled_groups = models.ManyToManyField(Group, through='GroupEnrolled', related_name="competition")

    type_of_competition = models.ForeignKey('TypeOfCompetition', blank=False)
    state_of_competition = models.CharField(choices=STATE, default='Register', max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __unicode__(self):
        return self.name


class TypeOfCompetition(models.Model):
    name = models.CharField(max_length=128, blank=False, unique=True, validators=[validate_slug])
    number_teams_for_trial = models.IntegerField(validators=[MinValueValidator(1)], blank=False, default=1)
    number_agents_by_grid = models.IntegerField(validators=[MinValueValidator(1)], blank=False, default=1)

    class Meta:
        unique_together = ('name', 'number_teams_for_trial', 'number_agents_by_grid',)

    def __unicode__(self):
        return self.name


class GroupEnrolled(models.Model):
    competition = models.ForeignKey(Competition, blank=False)
    group = models.ForeignKey(Group, blank=False)

    valid = models.BooleanField(default=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('competition', 'group',)
        ordering = ['created_at']

    def __unicode__(self):
        return self.group.name


class Round(models.Model):
    name = models.CharField(max_length=128, blank=False, unique=True, validators=[validate_slug])

    parent_competition = models.ForeignKey(Competition, blank=False)

    param_list_path = models.FileField(max_length=128)
    grid_path = models.FileField(max_length=128)
    lab_path = models.FileField(max_length=128)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        get_latest_by = "created_at"

    def __unicode__(self):
        return self.name


class Agent(models.Model):
    agent_name = models.CharField(max_length=128, blank=False, unique=True, validators=[validate_slug])
    user = models.ForeignKey(Account, blank=False)
    group = models.ForeignKey(Group, blank=False)
    locations = models.CharField(max_length=256)

    language = models.CharField(choices=settings.ALLOWED_UPLOAD_LANGUAGES, max_length=100)
    code_valid = models.BooleanField(default=True)
    is_virtual = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __unicode__(self):
        return self.agent_name


class PolePosition(models.Model):
    identifier = models.CharField(max_length=100, blank=False, unique=True, default=uuid.uuid4)
    competition = models.ForeignKey(Competition, blank=False)
    group = models.ForeignKey(Group, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('competition', 'group',)

    def __unicode__(self):
        return self.identifier


class AgentInstance(models.Model):
    agent = models.ForeignKey(Agent, blank=False)
    pole_position = models.ForeignKey(PolePosition, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CompetitionAgent(models.Model):
    competition = models.ForeignKey(Competition, blank=False)
    round = models.ForeignKey(Round, blank=False)
    agent = models.ForeignKey(Agent, blank=False)

    eligible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('competition', 'round', 'agent',)
        ordering = ['created_at']


class LogSimulationAgent(models.Model):
    competition_agent = models.ForeignKey('CompetitionAgent')
    simulation = models.ForeignKey('Simulation')

    pos = models.IntegerField(blank=False)

    class Meta:
        unique_together = ('competition_agent', 'simulation',)


class Simulation(models.Model):
    identifier = models.CharField(max_length=100, blank=False, unique=True, default=uuid.uuid4)

    round = models.ForeignKey(Round, blank=False)
    started = models.BooleanField(default=False)
    log_json = models.FileField(upload_to="json_logs/%Y/%m/%d")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        get_latest_by = "created_at"

    def __unicode__(self):
        return self.identifier