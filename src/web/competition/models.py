from django.db import models

from authentication.models import Account, Group


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