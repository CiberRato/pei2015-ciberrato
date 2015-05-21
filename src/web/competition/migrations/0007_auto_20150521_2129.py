# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_auto_20150519_1522'),
        ('competition', '0006_auto_20150519_1150'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgentScoreRound',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('number_of_agents', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('time', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('agent', models.ForeignKey(to='competition.Agent')),
                ('round', models.ForeignKey(to='competition.Round')),
                ('team', models.ForeignKey(to='authentication.Team')),
                ('trial', models.ForeignKey(to='competition.Trial')),
            ],
            options={
                'ordering': ('score', '-number_of_agents', 'time'),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='agentscoreround',
            unique_together=set([('trial', 'team')]),
        ),
    ]
