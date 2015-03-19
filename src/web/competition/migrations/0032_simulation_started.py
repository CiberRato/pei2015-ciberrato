# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0031_auto_20150318_1130'),
    ]

    operations = [
        migrations.AddField(
            model_name='simulation',
            name='started',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
