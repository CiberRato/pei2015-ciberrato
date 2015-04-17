# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0011_auto_20150415_1800'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='groupmember',
            unique_together=set([('account', 'group')]),
        ),
    ]
