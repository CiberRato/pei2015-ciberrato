# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import uuid


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StickyNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.CharField(default=uuid.uuid4, unique=True, max_length=100)),
                ('active', models.BooleanField(default=False)),
                ('time', models.IntegerField(default=5)),
                ('note', models.CharField(max_length=150, validators=[django.core.validators.MinLengthValidator(1)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['created_at'],
                'get_latest_by': 'created_at',
            },
            bases=(models.Model,),
        ),
    ]
