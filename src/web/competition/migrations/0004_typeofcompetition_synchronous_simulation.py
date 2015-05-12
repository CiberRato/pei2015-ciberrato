# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0003_auto_20150509_2148'),
    ]

    operations = [
        migrations.AddField(
            model_name='typeofcompetition',
            name='synchronous_simulation',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
