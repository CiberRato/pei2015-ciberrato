# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0011_auto_20150303_1600'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='agent_name',
            field=models.CharField(unique=True, max_length=128),
            preserve_default=True,
        ),
    ]
