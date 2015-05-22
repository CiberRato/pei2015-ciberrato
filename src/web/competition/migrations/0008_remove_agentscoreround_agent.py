# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0007_auto_20150521_2129'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='agentscoreround',
            name='agent',
        ),
    ]
