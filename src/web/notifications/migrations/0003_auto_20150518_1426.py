# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_oldadminnotification_oldbroadcastnotification_oldnoficationuser_oldnotificationteam'),
    ]

    operations = [
        migrations.AddField(
            model_name='oldbroadcastnotification',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 18, 14, 26, 39, 105720), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='oldnoficationuser',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 18, 14, 26, 47, 153349), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='oldnotificationteam',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 18, 14, 26, 51, 464151), auto_now_add=True),
            preserve_default=False,
        ),
    ]
