import uuid
from django.db import models

from authentication.models import Account, Group


class Competition(models.Model):
    name = models.CharField(max_length=128, blank=False, unique=True)

    COLABORATIVA = 'CB'
    COMPETITIVA = 'CP'

    TYPE_OF_COMPETITIONS = (
        (COLABORATIVA, 'Colaborativa'),
        (COMPETITIVA, 'Competitiva'),
    )

    REGISTER = 'RG'
    COMPETITION = 'CP'
    PAST = 'PST'

    STATE = (
        (REGISTER, 'Register'),
        (COMPETITION, 'Competition'),
        (PAST, 'Past'),
    )

    enrolled_groups = models.ManyToManyField(Group, through='GroupEnrolled', related_name="competition")

    type_of_competition = models.CharField(choices=TYPE_OF_COMPETITIONS, default='Colaborativa', max_length=100)
    state_of_competition = models.CharField(choices=STATE, default='Register', max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

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
    name = models.CharField(max_length=128, blank=False, unique=True)

    parent_competition = models.ForeignKey(Competition, blank=False)

    param_list_path = models.FileField(max_length=128)
    grid_path = models.FileField(max_length=128)
    lab_path = models.FileField(max_length=128)
    agents_list = models.ManyToManyField('Agent', through='CompetitionAgent', related_name="round")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        get_latest_by = "created_at"

    def __unicode__(self):
        return self.name


class Agent(models.Model):
    agent_name = models.CharField(max_length=128, blank=False)
    user = models.ForeignKey(Account, blank=False)
    group = models.ForeignKey(Group, blank=False)
    location = models.CharField(max_length=128, unique=True)

    code_valid = models.BooleanField(default=False, blank=False)

    competitions = models.ManyToManyField('Competition', through='CompetitionAgent', related_name="competition")
    rounds = models.ManyToManyField('Round', through='CompetitionAgent', related_name="round")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __unicode__(self):
        return self.agent_name


class CompetitionAgent(models.Model):
    competition = models.ForeignKey(Competition, blank=False)
    round = models.ForeignKey(Round, blank=False)
    agent = models.ForeignKey(Agent, blank=False)

    simulation = models.ForeignKey('Simulation')

    eligible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('competition', 'round', 'agent',)
        ordering = ['created_at']


class Simulation(models.Model):
    identifier = models.CharField(max_length=100, blank=False, unique=True, default=uuid.uuid4)

    round = models.ForeignKey(Round, blank=False)
    log_path = models.FileField(max_length=128)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __unicode__(self):
        return self.agent_path