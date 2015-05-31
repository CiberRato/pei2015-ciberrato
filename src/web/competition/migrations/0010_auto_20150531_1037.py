# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0009_auto_20150521_2206'),
    ]

    operations = [
        migrations.AddField(
            model_name='trial',
            name='execute_sh_log',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='trial',
            name='prepare_sh_log',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='agent',
            name='language',
            field=models.CharField(default=b'Python', max_length=100, choices=[(b'Python', b'Python'), (b'C++', b'cplusplus'), (b'Java', b'Java'), (b'Unknown', b'Unknown')]),
            preserve_default=True,
        ),
    ]
