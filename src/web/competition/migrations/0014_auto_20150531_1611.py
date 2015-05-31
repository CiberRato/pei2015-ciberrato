# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0013_auto_20150531_1409'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='agent',
            name='validation_execution_log',
        ),
        migrations.AlterField(
            model_name='agent',
            name='validation_result',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
    ]
