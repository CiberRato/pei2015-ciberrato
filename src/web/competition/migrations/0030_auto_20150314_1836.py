# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0029_auto_20150313_2108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simulation',
            name='log_json',
            field=models.FileField(upload_to=b'json_logs/%Y/%m/%d'),
            preserve_default=True,
        ),
    ]
