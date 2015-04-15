# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0045_remove_competitionagent_eligible'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='agentgrid',
            options={'ordering': ('position', 'grid_position')},
        ),
        migrations.AlterModelOptions(
            name='simulationgrid',
            options={'ordering': ('position', 'grid_positions', 'simulation')},
        ),
    ]
