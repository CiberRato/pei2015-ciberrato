# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0027_auto_20150307_1138'),
    ]

    operations = [
        migrations.RenameField(
            model_name='simulation',
            old_name='log',
            new_name='log_json',
        ),
        migrations.AddField(
            model_name='simulation',
            name='simulation_log_xml',
            field=models.TextField(default=None, max_length=128),
            preserve_default=False,
        ),
    ]
