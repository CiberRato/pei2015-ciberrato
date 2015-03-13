# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0028_auto_20150307_1828'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='simulation',
            name='simulation_log_xml',
        ),
        migrations.AlterField(
            model_name='competition',
            name='state_of_competition',
            field=models.CharField(default=b'Register', max_length=100, choices=[(b'Register', b'Register'), (b'Competition', b'Competition'), (b'Past', b'Past')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='competition',
            name='type_of_competition',
            field=models.CharField(default=b'Collaborative', max_length=100, choices=[(b'Collaborative', b'Collaborative'), (b'Competitive', b'Competitive')]),
            preserve_default=True,
        ),
    ]
