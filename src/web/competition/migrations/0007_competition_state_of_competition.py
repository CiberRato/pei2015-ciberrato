# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0006_auto_20150303_0951'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='state_of_competition',
            field=models.CharField(default=b'Register', max_length=100, choices=[(b'RG', b'Register'), (b'CP', b'Competition'), (b'PST', b'Past')]),
            preserve_default=True,
        ),
    ]
