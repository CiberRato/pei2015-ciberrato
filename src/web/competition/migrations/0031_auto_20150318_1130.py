# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0030_auto_20150314_1836'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='language',
            field=models.CharField(max_length=100, choices=[(b'Python', b'Python'), (b'C', b'C'), (b'C++', b'cplusplus'), (b'Java', b'Java')]),
            preserve_default=True,
        ),
    ]
