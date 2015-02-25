# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0002_auto_20150225_1805'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='competition',
            options={'ordering': ['created_at']},
        ),
        migrations.AddField(
            model_name='competition',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 25, 18, 10, 40, 947370, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='competition',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 25, 18, 10, 46, 874378, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
