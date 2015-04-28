# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0012_notificationbroadcast_broadcast_channel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notificationbroadcast',
            name='broadcast_channel',
        ),
    ]
