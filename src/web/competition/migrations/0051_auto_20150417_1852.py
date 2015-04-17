# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0012_auto_20150417_1348'),
        ('competition', '0050_auto_20150415_1800'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamScore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('number_of_agents', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('time', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('team', models.ForeignKey(to='authentication.Group')),
                ('trial', models.ForeignKey(to='competition.Simulation')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='teamscore',
            unique_together=set([('trial', 'team')]),
        ),
    ]
