# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_account_login_error'),
        ('competition', '0004_typeofcompetition_synchronous_simulation'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrivateCompetitionLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('team', models.ForeignKey(to='authentication.Team')),
                ('trial', models.ForeignKey(to='competition.Trial')),
            ],
            options={
                'ordering': ('created_at',),
            },
            bases=(models.Model,),
        ),
    ]
