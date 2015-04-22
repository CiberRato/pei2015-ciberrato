# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_auto_20150422_0847'),
        ('competition', '0004_auto_20150421_2114'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamEnrolled',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('valid', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('competition', models.ForeignKey(to='competition.Competition')),
                ('team', models.ForeignKey(to='authentication.Team')),
            ],
            options={
                'ordering': ['created_at'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='groupenrolled',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='groupenrolled',
            name='competition',
        ),
        migrations.RemoveField(
            model_name='groupenrolled',
            name='group',
        ),
        migrations.AlterUniqueTogether(
            name='teamenrolled',
            unique_together=set([('competition', 'team')]),
        ),
        migrations.RenameField(
            model_name='agent',
            old_name='group',
            new_name='team',
        ),
        migrations.RenameField(
            model_name='gridpositions',
            old_name='group',
            new_name='team',
        ),
        migrations.RemoveField(
            model_name='competition',
            name='enrolled_groups',
        ),
        migrations.DeleteModel(
            name='GroupEnrolled',
        ),
        migrations.AddField(
            model_name='competition',
            name='enrolled_teams',
            field=models.ManyToManyField(related_name='competition', through='competition.TeamEnrolled', to='authentication.Team'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='gridpositions',
            unique_together=set([('competition', 'team')]),
        ),
    ]
