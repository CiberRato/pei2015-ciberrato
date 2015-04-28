# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0013_remove_notificationbroadcast_broadcast_channel'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationbroadcast',
            name='broadcast',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
