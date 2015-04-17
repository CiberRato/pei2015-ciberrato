# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0051_auto_20150417_1852'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='validation_result',
            field=models.CharField(default=' ', max_length=512),
            preserve_default=False,
        ),
    ]
