# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
        ('notifications', '0009_auto_20150427_2206'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notificationteam',
            name='user',
        ),
        migrations.AddField(
            model_name='notificationteam',
            name='team',
            field=models.ForeignKey(default=0, to='authentication.Team'),
            preserve_default=False,
        ),
    ]
