# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competition',
            name='state_of_competition',
            field=models.CharField(default=b'Register', max_length=100, db_index=True, choices=[(b'Register', b'Register'), (b'Competition', b'Competition'), (b'Past', b'Past')]),
            preserve_default=True,
        ),
    ]
