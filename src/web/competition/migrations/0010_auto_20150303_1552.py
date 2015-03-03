# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0009_auto_20150303_1549'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='location',
            field=models.FilePathField(unique=True, max_length=128),
            preserve_default=True,
        ),
    ]
