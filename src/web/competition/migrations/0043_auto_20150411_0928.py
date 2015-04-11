# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0042_auto_20150411_0916'),
    ]

    operations = [
        migrations.CreateModel(
            name='SimulationGrid',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('grid_positions', models.ForeignKey(to='competition.GridPositions')),
                ('simulation', models.ForeignKey(to='competition.Simulation')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='gridgroups',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='gridgroups',
            name='grid_positions',
        ),
        migrations.RemoveField(
            model_name='gridgroups',
            name='simulation',
        ),
        migrations.DeleteModel(
            name='GridGroups',
        ),
        migrations.AlterUniqueTogether(
            name='simulationgrid',
            unique_together=set([('position', 'simulation')]),
        ),
    ]
