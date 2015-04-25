# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0003_auto_20150425_1408'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competition',
            name='allow_remote_agents',
            field=models.BooleanField(),
            preserve_default=True,
        ),
    ]
