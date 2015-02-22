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

