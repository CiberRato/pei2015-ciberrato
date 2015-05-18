# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_auto_20150518_1426'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='OldNoficationUser',
            new_name='OldNotificationUser',
        ),
    ]
