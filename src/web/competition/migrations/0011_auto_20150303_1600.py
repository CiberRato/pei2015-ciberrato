# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0010_auto_20150303_1552'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='agent',
            name='location',
        ),
        migrations.AddField(
            model_name='agent',
            name='locations',
            field=models.CharField(default=None, max_length=256),
            preserve_default=False,
        ),
    ]
