# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0015_auto_20150303_1950'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competitionagent',
            name='simulation',
            field=models.ForeignKey(blank=True, to='competition.Simulation', null=True),
            preserve_default=True,
        ),
    ]
