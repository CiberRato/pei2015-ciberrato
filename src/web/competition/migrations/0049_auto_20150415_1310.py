# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0048_auto_20150415_1256'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='agentgrid',
            unique_together=set([('position', 'grid_position')]),
        ),
        migrations.AlterUniqueTogether(
            name='simulationgrid',
            unique_together=set([('position', 'simulation')]),
        ),
    ]
