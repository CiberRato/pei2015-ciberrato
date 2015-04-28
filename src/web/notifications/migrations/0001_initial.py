# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import swampdragon.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationBroadcast',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField()),
                ('broadcast', models.IntegerField()),
            ],
            options={
            },
            bases=(swampdragon.models.SelfPublishModel, models.Model),
        ),
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
        migrations.CreateModel(
            name='NotificationUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(swampdragon.models.SelfPublishModel, models.Model),
        ),
    ]
