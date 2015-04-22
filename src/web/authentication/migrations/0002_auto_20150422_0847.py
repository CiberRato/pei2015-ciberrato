# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RenameModel(
            old_name='Group',
            new_name='Team',
        ),
        migrations.AlterUniqueTogether(
            name='groupmember',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='groupmember',
            name='account',
        ),
        migrations.RemoveField(
            model_name='groupmember',
            name='group',
        ),
        migrations.AddField(
            model_name='teammember',
            name='team',
            field=models.ForeignKey(to='authentication.Team'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='teammember',
            unique_together=set([('account', 'team')]),
        ),
        migrations.RemoveField(
            model_name='account',
            name='groups',
        ),
        migrations.DeleteModel(
            name='GroupMember',
        ),
        migrations.AddField(
            model_name='account',
            name='teams',
            field=models.ManyToManyField(related_name='account', through='authentication.TeamMember', to='authentication.Team'),
            preserve_default=True,
        ),
    ]
