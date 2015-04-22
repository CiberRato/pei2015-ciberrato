# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import re
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('email', models.EmailField(unique=True, max_length=75, validators=[django.core.validators.EmailValidator])),
                ('username', models.CharField(unique=True, max_length=40, validators=[django.core.validators.RegexValidator(re.compile(b'^[-a-zA-Z0-9_ ]+$'), b'Enter a valid word consisting of letters, numbers, underscores, spaces or hyphens.', b'invalid'), django.core.validators.MinLengthValidator(2)])),
                ('first_name', models.CharField(max_length=40, validators=[django.core.validators.RegexValidator(re.compile(b'^[-a-zA-Z0-9_ ]+$'), b'Enter a valid word consisting of letters, numbers, underscores, spaces or hyphens.', b'invalid'), django.core.validators.MinLengthValidator(2)])),
                ('last_name', models.CharField(max_length=40, validators=[django.core.validators.RegexValidator(re.compile(b'^[-a-zA-Z0-9_ ]+$'), b'Enter a valid word consisting of letters, numbers, underscores, spaces or hyphens.', b'invalid'), django.core.validators.MinLengthValidator(2)])),
                ('teaching_institution', models.CharField(max_length=140, validators=[django.core.validators.MinLengthValidator(2)])),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128, validators=[django.core.validators.RegexValidator(re.compile(b'^[-a-zA-Z0-9_ ]+$'), b'Enter a valid word consisting of letters, numbers, underscores, spaces or hyphens.', b'invalid'), django.core.validators.MinLengthValidator(1)])),
                ('max_members', models.IntegerField(default=5, validators=[django.core.validators.MinValueValidator(1)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('team', models.ForeignKey(to='authentication.Team')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='teammember',
            unique_together=set([('account', 'team')]),
        ),
        migrations.AddField(
            model_name='account',
            name='teams',
            field=models.ManyToManyField(related_name='account', through='authentication.TeamMember', to='authentication.Team'),
            preserve_default=True,
        ),
    ]
