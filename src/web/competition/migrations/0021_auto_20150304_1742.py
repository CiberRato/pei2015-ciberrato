# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0020_agent_language'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='language',
            field=models.CharField(max_length=100, choices=[(b'py', b'Python'), (b'c', b'C'), (b'c++', b'cplusplus'), (b'java', b'Java')]),
            preserve_default=True,
        ),
    ]
