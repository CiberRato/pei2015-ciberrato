# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0003_auto_20150501_2227'),
    ]

    operations = [
        migrations.RenameField(
            model_name='round',
            old_name='grid_path_can_delete',
            new_name='grid_can_delete',
        ),
        migrations.RenameField(
            model_name='round',
            old_name='lab_path_can_delete',
            new_name='lab_can_delete',
        ),
        migrations.RenameField(
            model_name='round',
            old_name='param_list_can_delete',
            new_name='param_can_delete',
        ),
    ]
