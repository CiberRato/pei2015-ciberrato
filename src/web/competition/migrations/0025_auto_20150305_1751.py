# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0024_auto_20150304_2150'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='logsimulationagent',
            unique_together=set([('competition_agent', 'simulation')]),
        ),
    ]
