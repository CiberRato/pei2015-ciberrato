# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0004_auto_20150423_2233'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='allow_remote_agents',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
