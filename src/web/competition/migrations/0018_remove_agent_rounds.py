# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0017_auto_20150303_1954'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='agent',
            name='rounds',
        ),
    ]
