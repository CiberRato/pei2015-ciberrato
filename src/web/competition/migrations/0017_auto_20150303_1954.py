# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0016_auto_20150303_1951'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogSimulationAgent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('competition_agent', models.ForeignKey(to='competition.CompetitionAgent')),
                ('simulation', models.ForeignKey(to='competition.Simulation')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='competitionagent',
            name='simulation',
        ),
    ]
