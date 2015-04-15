# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import re
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0006_auto_20150412_1121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='email',
            field=models.EmailField(unique=True, max_length=75, validators=[django.core.validators.EmailValidator]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='first_name',
            field=models.CharField(max_length=40, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+$'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid'), django.core.validators.MinLengthValidator(2)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='last_name',
            field=models.CharField(max_length=40, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+$'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid'), django.core.validators.MinLengthValidator(2)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='teaching_institution',
            field=models.CharField(max_length=140, validators=[django.core.validators.MinLengthValidator(2)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='username',
            field=models.CharField(unique=True, max_length=40, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+$'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid'), django.core.validators.MinLengthValidator(2)]),
            preserve_default=True,
        ),
    ]
