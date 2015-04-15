# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_auto_20150322_1032'),
        ('competition', '0040_agentpole_position'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgentGrid',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('agent', models.ForeignKey(to='competition.Agent')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GridPositions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.CharField(default=uuid.uuid4, unique=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('competition', models.ForeignKey(to='competition.Competition')),
                ('group', models.ForeignKey(to='authentication.Group')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='agentpole',
            name='agent',
        ),
        migrations.RemoveField(
            model_name='agentpole',
            name='pole_position',
        ),
        migrations.DeleteModel(
            name='AgentPole',
        ),
        migrations.AlterUniqueTogether(
            name='poleposition',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='poleposition',
            name='competition',
        ),
        migrations.RemoveField(
            model_name='poleposition',
            name='group',
        ),
        migrations.DeleteModel(
            name='PolePosition',
        ),
        migrations.AlterUniqueTogether(
            name='gridpositions',
            unique_together=set([('competition', 'group')]),
        ),
        migrations.AddField(
            model_name='agentgrid',
            name='grid_position',
            field=models.ForeignKey(to='competition.GridPositions'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='agentgrid',
            unique_together=set([('position', 'grid_position')]),
        ),
    ]
