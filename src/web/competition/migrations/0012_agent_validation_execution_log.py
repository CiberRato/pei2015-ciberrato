# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0011_auto_20150531_1330'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='validation_execution_log',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
