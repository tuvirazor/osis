# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-02-02 14:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0226_auto_20180202_1044'),
    ]

    operations = [
        migrations.RenameField(
            model_name='entitycomponentyear',
            old_name='hourly_volume_partial',
            new_name='repartition_volume',
        ),
        migrations.RemoveField(
            model_name='entitycomponentyear',
            name='hourly_volume_total',
        ),
    ]
