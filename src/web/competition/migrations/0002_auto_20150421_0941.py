# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='code_valid',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]