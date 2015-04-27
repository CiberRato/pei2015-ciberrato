# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import swampdragon.models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
        ('notifications', '0007_auto_20150427_1813'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationTeam',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField()),
                ('team', models.ForeignKey(to='authentication.Team')),
            ],
            options={
            },
            bases=(swampdragon.models.SelfPublishModel, models.Model),
        ),
    ]
