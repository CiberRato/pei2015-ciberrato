# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0038_auto_20150409_1817'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgentPole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('agent', models.ForeignKey(to='competition.Agent')),
                ('pole_position', models.ForeignKey(to='competition.PolePosition')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='agentinstance',
            name='agent',
        ),
        migrations.RemoveField(
            model_name='agentinstance',
            name='pole_position',
        ),
        migrations.DeleteModel(
            name='AgentInstance',
        ),
    ]
