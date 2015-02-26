# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0003_remove_competition_rounds'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='competitionagent',
            name='group',
        ),
    ]
