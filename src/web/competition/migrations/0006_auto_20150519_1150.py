# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0005_privatecompetitionlog'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='privatecompetitionlog',
            unique_together=set([('trial', 'team')]),
        ),
    ]
