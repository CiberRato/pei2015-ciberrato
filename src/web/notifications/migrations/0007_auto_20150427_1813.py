# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0006_notification_user'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Notification',
            new_name='NotificationUser',
        ),
    ]
