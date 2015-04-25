# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import re
from django.conf import settings
import django.core.validators
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('agent_name', models.CharField(unique=True, max_length=128, validators=[django.core.validators.RegexValidator(re.compile(b'^[-a-zA-Z0-9_ ]+$'), b'Enter a valid word consisting of letters, numbers, underscores, spaces or hyphens.', b'invalid'), django.core.validators.MinLengthValidator(1)])),
                ('language', models.CharField(default=b'Python', max_length=100, choices=[(b'Python', b'Python'), (b'C', b'C'), (b'C++', b'cplusplus'), (b'Java', b'Java')])),
                ('code_valid', models.BooleanField(default=False)),
                ('validation_result', models.CharField(max_length=512)),
                ('is_local', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('team', models.ForeignKey(to='authentication.Team')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created_at'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AgentFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=b'agents/%Y/%m/%d')),
                ('original_name', models.CharField(max_length=128)),
                ('agent', models.ForeignKey(to='competition.Agent')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
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
                'ordering': ('position', 'grid_position'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128, validators=[django.core.validators.RegexValidator(re.compile(b'^[-a-zA-Z0-9_ ]+$'), b'Enter a valid word consisting of letters, numbers, underscores, spaces or hyphens.', b'invalid'), django.core.validators.MinLengthValidator(1)])),
                ('allow_remote_agents', models.BooleanField(default=False)),
                ('state_of_competition', models.CharField(default=b'Register', max_length=100, choices=[(b'Register', b'Register'), (b'Competition', b'Competition'), (b'Past', b'Past')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['created_at'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CompetitionAgent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('agent', models.ForeignKey(to='competition.Agent')),
                ('competition', models.ForeignKey(to='competition.Competition')),
            ],
            options={
                'ordering': ['created_at'],
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
                ('team', models.ForeignKey(to='authentication.Team')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
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
            name='Round',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128, validators=[django.core.validators.RegexValidator(re.compile(b'^[-a-zA-Z0-9_ ]+$'), b'Enter a valid word consisting of letters, numbers, underscores, spaces or hyphens.', b'invalid'), django.core.validators.MinLengthValidator(1)])),
                ('param_list_path', models.FileField(upload_to=b'params/%Y/%m/%d')),
                ('grid_path', models.FileField(upload_to=b'grids/%Y/%m/%d')),
                ('lab_path', models.FileField(upload_to=b'labs/%Y/%m/%d')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('parent_competition', models.ForeignKey(to='competition.Competition')),
            ],
            options={
                'ordering': ['created_at'],
                'get_latest_by': 'created_at',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TeamEnrolled',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('valid', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('competition', models.ForeignKey(to='competition.Competition')),
                ('team', models.ForeignKey(to='authentication.Team')),
            ],
            options={
                'ordering': ['created_at'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TeamScore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('number_of_agents', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('time', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('team', models.ForeignKey(to='authentication.Team')),
            ],
            options={
                'ordering': ('score', '-number_of_agents', 'time'),
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
        migrations.CreateModel(
            name='TypeOfCompetition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128, validators=[django.core.validators.RegexValidator(re.compile(b'^[-a-zA-Z0-9_ ]+$'), b'Enter a valid word consisting of letters, numbers, underscores, spaces or hyphens.', b'invalid'), django.core.validators.MinLengthValidator(1)])),
                ('number_teams_for_trial', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('number_agents_by_grid', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('single_position', models.BooleanField(default=False)),
                ('timeout', models.IntegerField(default=5, validators=[django.core.validators.MinValueValidator(0)])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='typeofcompetition',
            unique_together=set([('name', 'number_teams_for_trial', 'number_agents_by_grid')]),
        ),
        migrations.AlterUniqueTogether(
            name='trialgrid',
            unique_together=set([('position', 'trial')]),
        ),
        migrations.AddField(
            model_name='teamscore',
            name='trial',
            field=models.ForeignKey(to='competition.Trial'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='teamscore',
            unique_together=set([('trial', 'team')]),
        ),
        migrations.AlterUniqueTogether(
            name='teamenrolled',
            unique_together=set([('competition', 'team')]),
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
        migrations.AlterUniqueTogether(
            name='gridpositions',
            unique_together=set([('competition', 'team')]),
        ),
        migrations.AddField(
            model_name='competitionagent',
            name='round',
            field=models.ForeignKey(to='competition.Round'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='competitionagent',
            unique_together=set([('competition', 'round', 'agent')]),
        ),
        migrations.AddField(
            model_name='competition',
            name='enrolled_teams',
            field=models.ManyToManyField(related_name='competition', through='competition.TeamEnrolled', to='authentication.Team'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='competition',
            name='type_of_competition',
            field=models.ForeignKey(to='competition.TypeOfCompetition'),
            preserve_default=True,
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
        migrations.AlterUniqueTogether(
            name='agentfile',
            unique_together=set([('agent', 'original_name')]),
        ),
    ]
