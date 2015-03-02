# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0004_auto_20150228_1320'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='round',
            options={'ordering': ['created_at'], 'get_latest_by': 'created_at'},
        ),
        migrations.RemoveField(
            model_name='simulation',
            name='agent_path',
        ),
        migrations.RemoveField(
            model_name='simulation',
            name='grid_path',
        ),
        migrations.RemoveField(
            model_name='simulation',
            name='group',
        ),
        migrations.RemoveField(
            model_name='simulation',
            name='lab_path',
        ),
        migrations.RemoveField(
            model_name='simulation',
            name='param_list_path',
        ),
        migrations.RemoveField(
            model_name='simulation',
            name='sent',
        ),
        migrations.RemoveField(
            model_name='simulation',
            name='user',
        ),
        migrations.AddField(
            model_name='competitionagent',
            name='simulation',
            field=models.ForeignKey(default=None, to='competition.Simulation'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='simulation',
            name='identifier',
            field=models.CharField(default=uuid.uuid4, unique=True, max_length=100),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='simulation',
            name='log_path',
            field=models.FileField(default=None, max_length=128, upload_to=b''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='simulation',
            name='round',
            field=models.ForeignKey(default=None, to='competition.Round'),
            preserve_default=False,
        ),
    ]
