# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0025_auto_20150305_1751'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='simulation',
            options={'ordering': ['created_at'], 'get_latest_by': 'created_at'},
        ),
        migrations.AddField(
            model_name='simulation',
            name='pos',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
