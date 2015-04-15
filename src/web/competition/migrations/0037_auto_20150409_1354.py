# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0036_auto_20150409_1303'),
    ]

    operations = [
        migrations.RenameField(
            model_name='typeofcompetition',
            old_name='nome',
            new_name='name',
        ),
        migrations.AlterUniqueTogether(
            name='typeofcompetition',
            unique_together=set([('name', 'number_teams_for_trial', 'number_agents_by_grid')]),
        ),
    ]
