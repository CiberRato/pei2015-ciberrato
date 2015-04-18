# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0053_auto_20150418_0901'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='teamscore',
            options={'ordering': ('score', '-number_of_agents', 'time')},
        ),
    ]
