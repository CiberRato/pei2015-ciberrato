# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0008_auto_20150425_1953'),
    ]

    operations = [
        migrations.AddField(
            model_name='trial',
            name='started',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
