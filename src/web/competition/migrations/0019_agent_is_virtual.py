# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0018_remove_agent_rounds'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='is_virtual',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
