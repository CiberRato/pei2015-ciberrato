# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import re
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0046_auto_20150414_1037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='agent_name',
            field=models.CharField(unique=True, max_length=128, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+$'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid'), django.core.validators.MinLengthValidator(1)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='competition',
            name='name',
            field=models.CharField(unique=True, max_length=128, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+$'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid'), django.core.validators.MinLengthValidator(1)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='round',
            name='name',
            field=models.CharField(unique=True, max_length=128, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+$'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid'), django.core.validators.MinLengthValidator(1)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='typeofcompetition',
            name='name',
            field=models.CharField(unique=True, max_length=128, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+$'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid'), django.core.validators.MinLengthValidator(1)]),
            preserve_default=True,
        ),
    ]
