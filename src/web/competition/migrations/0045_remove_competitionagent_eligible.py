# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0044_auto_20150412_0838'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='competitionagent',
            name='eligible',
        ),
    ]
