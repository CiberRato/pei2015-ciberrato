# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0005_auto_20150425_1619'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='round',
            unique_together=set([('name', 'parent_competition')]),
        ),
    ]
