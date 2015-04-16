# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0047_auto_20150414_1806'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='agentgrid',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='simulationgrid',
            unique_together=set([]),
        ),
    ]
