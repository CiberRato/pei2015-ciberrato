# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0056_auto_20150418_1054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='code_valid',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
