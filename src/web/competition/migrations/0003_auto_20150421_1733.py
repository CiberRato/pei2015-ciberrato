# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0002_auto_20150421_0941'),
    ]

    operations = [
        migrations.AddField(
            model_name='simulation',
            name='errors',
            field=models.CharField(default=' ', max_length=150),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='simulation',
            name='waiting',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
