# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stickynote', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stickynote',
            name='active',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
