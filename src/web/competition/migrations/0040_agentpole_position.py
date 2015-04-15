# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0039_auto_20150410_1327'),
    ]

    operations = [
        migrations.AddField(
            model_name='agentpole',
            name='position',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(1)]),
            preserve_default=False,
        ),
    ]
