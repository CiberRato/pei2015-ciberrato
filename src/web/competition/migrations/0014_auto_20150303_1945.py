# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0013_auto_20150303_1943'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competitionagent',
            name='simulation',
            field=models.ForeignKey(to='competition.Simulation'),
            preserve_default=True,
        ),
    ]
