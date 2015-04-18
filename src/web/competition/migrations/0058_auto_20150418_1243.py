# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0057_auto_20150418_1128'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgentFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=b'agents/%Y/%m/%d')),
                ('agent', models.ForeignKey(to='competition.Agent')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='round',
            name='grid_path',
            field=models.FileField(upload_to=b'grids/%Y/%m/%d'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='round',
            name='lab_path',
            field=models.FileField(upload_to=b'labs/%Y/%m/%d'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='round',
            name='param_list_path',
            field=models.FileField(upload_to=b'params/%Y/%m/%d'),
            preserve_default=True,
        ),
    ]
