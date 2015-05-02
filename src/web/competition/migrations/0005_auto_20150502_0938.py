# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0004_auto_20150501_2232'),
    ]

    operations = [
        migrations.RenameField(
            model_name='round',
            old_name='param_can_delete',
            new_name='param_list_can_delete',
        ),
    ]
