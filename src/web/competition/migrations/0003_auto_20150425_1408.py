# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0002_auto_20150425_1408'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='language',
            field=models.CharField(default=b'Python', max_length=100, choices=[(b'Python', b'Python'), (b'C', b'C'), (b'C++', b'cplusplus'), (b'Java', b'Java'), (b'Unknown', b'Unknown')]),
            preserve_default=True,
        ),
    ]