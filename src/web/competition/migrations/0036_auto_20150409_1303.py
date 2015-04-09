# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import re
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0035_auto_20150324_1054'),
    ]

    operations = [
        migrations.CreateModel(
            name='TypeOfCompetition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(unique=True, max_length=128, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+$'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')])),
                ('number_teams_for_trial', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('number_agents_by_grid', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='typeofcompetition',
            unique_together=set([('nome', 'number_teams_for_trial', 'number_agents_by_grid')]),
        ),
        migrations.AlterField(
            model_name='competition',
            name='type_of_competition',
            field=models.ForeignKey(to='competition.TypeOfCompetition'),
            preserve_default=True,
        ),
    ]
