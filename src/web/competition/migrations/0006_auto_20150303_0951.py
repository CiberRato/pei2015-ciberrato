# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0005_auto_20150302_1950'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='code_valid',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='groupenrolled',
            name='valid',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
