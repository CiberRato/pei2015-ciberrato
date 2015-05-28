# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_auto_20150519_1522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='first_name',
            field=models.CharField(max_length=40, validators=[django.core.validators.MinLengthValidator(2)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='last_name',
            field=models.CharField(max_length=40, validators=[django.core.validators.MinLengthValidator(2)]),
            preserve_default=True,
        ),
    ]
