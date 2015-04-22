# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='typeofcompetition',
            name='single_position',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='typeofcompetition',
            name='timeout',
            field=models.IntegerField(default=5, validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=True,
        ),
    ]
