# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0002_auto_20150429_0929'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='grid_path_can_delete',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='round',
            name='lab_path_can_delete',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='round',
            name='param_list_can_delete',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
