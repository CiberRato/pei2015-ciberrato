# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0002_auto_20150225_2031'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='competition',
            name='rounds',
        ),
    ]
