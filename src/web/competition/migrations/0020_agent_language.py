# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0019_agent_is_virtual'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='language',
            field=models.CharField(default='c', max_length=100, choices=[(b'py', b'Python'), (b'c', b'C'), (b'c++', b'C++'), (b'java', b'Java')]),
            preserve_default=False,
        ),
    ]
