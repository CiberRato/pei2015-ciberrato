# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0032_simulation_started'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='agent',
            name='competitions',
        ),
        migrations.RemoveField(
            model_name='agent',
            name='rounds',
        ),
        migrations.RemoveField(
            model_name='round',
            name='agents_list',
        ),
    ]
