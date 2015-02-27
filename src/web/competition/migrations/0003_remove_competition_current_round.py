# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0002_auto_20150226_2206'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='competition',
            name='current_round',
        ),
    ]
