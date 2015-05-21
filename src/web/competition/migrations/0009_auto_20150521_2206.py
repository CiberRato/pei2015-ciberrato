# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0008_remove_agentscoreround_agent'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='agentscoreround',
            unique_together=set([('round', 'team')]),
        ),
    ]
