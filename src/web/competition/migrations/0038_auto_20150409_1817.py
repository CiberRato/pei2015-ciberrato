# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_auto_20150322_1032'),
        ('competition', '0037_auto_20150409_1354'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgentInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('agent', models.ForeignKey(to='competition.Agent')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PolePosition',
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
        migrations.AlterUniqueTogether(
            name='poleposition',
            unique_together=set([('competition', 'group')]),
        ),
        migrations.AddField(
            model_name='agentinstance',
            name='pole_position',
            field=models.ForeignKey(to='competition.PolePosition'),
            preserve_default=True,
        ),
    ]
