# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0002_auto_20150507_2210'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='competition',
            name='allow_remote_agents',
        ),
        migrations.AddField(
            model_name='typeofcompetition',
            name='allow_remote_agents',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
