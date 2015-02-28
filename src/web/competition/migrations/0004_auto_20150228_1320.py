# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_auto_20150225_1805'),
        ('competition', '0003_remove_competition_current_round'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupEnrolled',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('competition', models.ForeignKey(to='competition.Competition')),
                ('group', models.ForeignKey(to='authentication.Group')),
            ],
            options={
                'ordering': ['created_at'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='groupenrolled',
            unique_together=set([('competition', 'group')]),
        ),
        migrations.AddField(
            model_name='competition',
            name='enrolled_groups',
            field=models.ManyToManyField(related_name='competition', through='competition.GroupEnrolled', to='authentication.Group'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='competition',
            name='name',
            field=models.CharField(unique=True, max_length=128),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='round',
            name='name',
            field=models.CharField(unique=True, max_length=128),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='competitionagent',
            unique_together=set([('competition', 'round', 'agent')]),
        ),
    ]
