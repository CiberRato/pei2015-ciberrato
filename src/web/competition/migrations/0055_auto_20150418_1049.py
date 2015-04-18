# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0054_auto_20150418_0941'),
    ]

    operations = [
        migrations.RenameField(
            model_name='agent',
            old_name='is_virtual',
            new_name='is_local',
        ),
    ]
