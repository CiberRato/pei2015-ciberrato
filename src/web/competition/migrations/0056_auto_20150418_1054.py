# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0055_auto_20150418_1049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='code_valid',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
