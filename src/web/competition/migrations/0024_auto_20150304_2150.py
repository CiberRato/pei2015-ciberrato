# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0023_agent_rounds'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='simulation',
            name='log_path',
        ),
        migrations.AddField(
            model_name='simulation',
            name='log',
            field=models.TextField(default=None, max_length=128),
            preserve_default=False,
        ),
    ]
