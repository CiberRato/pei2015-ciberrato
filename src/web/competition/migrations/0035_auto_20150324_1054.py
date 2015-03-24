# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0034_auto_20150322_1032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='code_valid',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
