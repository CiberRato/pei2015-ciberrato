# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import swampdragon.models


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0009_auto_20150521_2206'),
        ('notifications', '0004_auto_20150518_1432'),
    ]

    operations = [
        migrations.CreateModel(
            name='StreamTrial',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField()),
                ('trial', models.ForeignKey(to='competition.Trial')),
            ],
            options={
            },
            bases=(swampdragon.models.SelfPublishModel, models.Model),
        ),
    ]
