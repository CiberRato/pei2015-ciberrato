# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0022_auto_20150304_1752'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='rounds',
            field=models.ManyToManyField(related_name='round', through='competition.CompetitionAgent', to='competition.Round'),
            preserve_default=True,
        ),
    ]
