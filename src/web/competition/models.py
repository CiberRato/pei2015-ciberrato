from django.db import models

from authentication.models import Account, Group


class Competition(models.Model):
    name = models.CharField(max_length=128, blank=False)
    rounds = models.ManyToManyField('Round', through='Round', related_name="competition")

    COBOLORATIVA = 'CB'
    COMPETITIVA = 'CP'

    TYPE_OF_COMPETITIONS = (
        (COBOLORATIVA, 'Cobolorativa'),
        (COMPETITIVA, 'Competitiva'),
    )

    type_of_competition = models.CharField(choices=TYPE_OF_COMPETITIONS, default='Cobolorativa', max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __unicode__(self):
        return self.name


class Round(models.Model):
    name = models.CharField(max_length=128, blank=False)

    competition = models.ForeignKey(Competition, blank=False)

    param_list_path = models.FileField(max_length=128)
    grid_path = models.FileField(max_length=128)
    lab_path = models.FileField(max_length=128)
    agents_list = models.ManyToManyField('Agent', through='CompetitionAgent', related_name="round")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __unicode__(self):
        return self.name


class Agent(models.Model):
    agent_name = models.CharField(max_length=128, blank=False)
    user = models.ForeignKey(Account, blank=False)
    group = models.ForeignKey(Group, blank=False)
    location = models.CharField(max_length=128, unique=True, blank=False)

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
    group = models.ForeignKey(Group, blank=False)

    eligible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

"""
---------------------------------------------------------------
APAGAR A PARTE DA SIMULATION QUANDO AS RONDAS ESTIVEREM PRONTAS
---------------------------------------------------------------
"""
class Simulation(models.Model):
    """
    Each simulation have a User (User that made the simulation request) and the group
    that this simulation belongs.
    The "sent" field shows when the simulation was retrieved by the server side.
    """
    user = models.ForeignKey(Account, blank=False)
    group = models.ForeignKey(Group, blank=False)

    sent = models.BooleanField(default=False)

    param_list_path = models.URLField(max_length=128)
    grid_path = models.URLField(max_length=128)
    lab_path = models.URLField(max_length=128)
    agent_path = models.URLField(max_length=128)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __unicode__(self):
        return self.agent_path