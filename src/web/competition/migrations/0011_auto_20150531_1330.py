# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0010_auto_20150531_1037'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trial',
            old_name='execute_sh_log',
            new_name='execution_log',
        ),
        migrations.RemoveField(
            model_name='trial',
            name='prepare_sh_log',
        ),
    ]
