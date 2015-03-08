# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0026_auto_20150307_1135'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='simulation',
            name='pos',
        ),
        migrations.AddField(
            model_name='logsimulationagent',
            name='pos',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
