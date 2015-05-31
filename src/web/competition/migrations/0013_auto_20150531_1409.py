# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0012_agent_validation_execution_log'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='validation_execution_log',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
    ]
