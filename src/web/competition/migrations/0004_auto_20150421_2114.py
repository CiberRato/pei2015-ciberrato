# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0003_auto_20150421_1733'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogTrialAgent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pos', models.IntegerField()),
                ('competition_agent', models.ForeignKey(to='competition.CompetitionAgent')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Trial',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.CharField(default=uuid.uuid4, unique=True, max_length=100)),
                ('started', models.BooleanField(default=False)),
                ('waiting', models.BooleanField(default=False)),
                ('errors', models.CharField(max_length=150)),
                ('log_json', models.FileField(upload_to=b'json_logs/%Y/%m/%d')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('round', models.ForeignKey(to='competition.Round')),
            ],
            options={
                'ordering': ['created_at'],
                'get_latest_by': 'created_at',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrialGrid',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('grid_positions', models.ForeignKey(to='competition.GridPositions')),
                ('trial', models.ForeignKey(to='competition.Trial')),
            ],
            options={
                'ordering': ('position', 'grid_positions', 'trial'),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='logsimulationagent',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='logsimulationagent',
            name='competition_agent',
        ),
        migrations.RemoveField(
            model_name='logsimulationagent',
            name='simulation',
        ),
        migrations.DeleteModel(
            name='LogSimulationAgent',
        ),
        migrations.RemoveField(
            model_name='simulation',
            name='round',
        ),
        migrations.AlterUniqueTogether(
            name='simulationgrid',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='simulationgrid',
            name='grid_positions',
        ),
        migrations.RemoveField(
            model_name='simulationgrid',
            name='simulation',
        ),
        migrations.DeleteModel(
            name='SimulationGrid',
        ),
        migrations.AlterUniqueTogether(
            name='trialgrid',
            unique_together=set([('position', 'trial')]),
        ),
        migrations.AddField(
            model_name='logtrialagent',
            name='trial',
            field=models.ForeignKey(to='competition.Trial'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='logtrialagent',
            unique_together=set([('pos', 'trial')]),
        ),
        migrations.AlterField(
            model_name='teamscore',
            name='trial',
            field=models.ForeignKey(to='competition.Trial'),
            preserve_default=True,
        ),
        migrations.DeleteModel(
            name='Simulation',
        ),
    ]
