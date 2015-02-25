# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_auto_20150222_1241'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='max_members',
            field=models.IntegerField(default=5, validators=[django.core.validators.MinValueValidator(1)]),
            preserve_default=True,
        ),
    ]
