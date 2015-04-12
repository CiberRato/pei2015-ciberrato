# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0043_auto_20150411_0928'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='agentgrid',
            options={'ordering': ['grid_position']},
        ),
        migrations.AlterModelOptions(
            name='simulationgrid',
            options={'ordering': ['position']},
        ),
        migrations.AlterUniqueTogether(
            name='logsimulationagent',
            unique_together=set([('pos', 'simulation')]),
        ),
    ]
