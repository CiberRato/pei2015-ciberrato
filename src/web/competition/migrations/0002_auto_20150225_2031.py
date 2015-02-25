# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('authentication', '0003_auto_20150225_1805'),
        ('competition', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('agent_name', models.CharField(max_length=128)),
                ('location', models.CharField(unique=True, max_length=128)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['created_at'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('type_of_competition', models.CharField(default=b'Colaborativa', max_length=100, choices=[(b'CB', b'Colaborativa'), (b'CP', b'Competitiva')])),
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
                ('eligible', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('agent', models.ForeignKey(to='competition.Agent')),
                ('competition', models.ForeignKey(to='competition.Competition')),
                ('group', models.ForeignKey(to='authentication.Group')),
            ],
            options={
                'ordering': ['created_at'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Round',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('param_list_path', models.FileField(max_length=128, upload_to=b'')),
                ('grid_path', models.FileField(max_length=128, upload_to=b'')),
                ('lab_path', models.FileField(max_length=128, upload_to=b'')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('agents_list', models.ManyToManyField(related_name='round', through='competition.CompetitionAgent', to='competition.Agent')),
                ('parent_competition', models.ForeignKey(to='competition.Competition')),
            ],
            options={
                'ordering': ['created_at'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='competitionagent',
            name='round',
            field=models.ForeignKey(to='competition.Round'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='competition',
            name='rounds',
            field=models.ManyToManyField(to='competition.Round'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='agent',
            name='competitions',
            field=models.ManyToManyField(related_name='competition', through='competition.CompetitionAgent', to='competition.Competition'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='agent',
            name='group',
            field=models.ForeignKey(to='authentication.Group'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='agent',
            name='rounds',
            field=models.ManyToManyField(related_name='round', through='competition.CompetitionAgent', to='competition.Round'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='agent',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='simulation',
            name='agent_path',
            field=models.URLField(max_length=128),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='simulation',
            name='grid_path',
            field=models.URLField(max_length=128),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='simulation',
            name='lab_path',
            field=models.URLField(max_length=128),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='simulation',
            name='param_list_path',
            field=models.URLField(max_length=128),
            preserve_default=True,
        ),
    ]
